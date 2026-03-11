import Foundation
import CryptoKit

// MARK: - Конфиг API

enum APIConfig {
    // ВАЖНО: подставь сюда URL своего backend
    static let baseURL = URL(string: "http://127.0.0.1:8081")! // или твой домен/адрес
    
    // ВАЖНО: значения должны совпадать с os.getenv("api") и os.getenv("signature") на backend
    static let apiKey = "YOUR_X_API_KEY_HERE"
    static let signatureSecret = "YOUR_SIGNATURE_SECRET_HERE"
}

// MARK: - Модели

struct AuthTokens: Codable {
    let access_token: String
    let refresh_token: String
    let token_type: String
}

// Подправь под фактический ответ /identify
struct IdentifyResult: Codable {
    let result: String?
}

// MARK: - Хранилище токенов (упрощённо через UserDefaults)

final class TokenStorage {
    private let accessKey = "access_token"
    private let refreshKey = "refresh_token"
    
    var accessToken: String? {
        get { UserDefaults.standard.string(forKey: accessKey) }
        set {
            if let v = newValue {
                UserDefaults.standard.set(v, forKey: accessKey)
            } else {
                UserDefaults.standard.removeObject(forKey: accessKey)
            }
        }
    }
    
    var refreshToken: String? {
        get { UserDefaults.standard.string(forKey: refreshKey) }
        set {
            if let v = newValue {
                UserDefaults.standard.set(v, forKey: refreshKey)
            } else {
                UserDefaults.standard.removeObject(forKey: refreshKey)
            }
        }
    }
    
    func save(tokens: AuthTokens) {
        accessToken = tokens.access_token
        refreshToken = tokens.refresh_token
    }
    
    func clear() {
        accessToken = nil
        refreshToken = nil
    }
}

// MARK: - HMAC‑подпись как в backend

func generateSignature(username: String, password: String, timestamp: String) -> String {
    // backend делает json.dumps(data_to_verify, sort_keys=True, separators=(',', ':'))
    let dict: [String: String] = [
        "password": password,
        "username": username
    ]
    
    let sortedKeys = dict.keys.sorted()
    var components: [String] = []
    for key in sortedKeys {
        if let value = dict[key] {
            let k = #"\"\#(key)\""#
            let v = #"\"\#(value)\""#
            components.append("\(k):\(v)")
        }
    }
    let json = "{\(components.joined(separator: ","))}"
    
    let keyData = Data(APIConfig.signatureSecret.utf8)
    let messageData = Data(json.utf8)
    
    let key = SymmetricKey(data: keyData)
    let signature = HMAC<SHA256>.authenticationCode(for: messageData, using: key)
    return signature.map { String(format: "%02x", $0) }.joined()
}

// MARK: - Ошибки

enum APIError: Error {
    case invalidResponse
    case http(Int)
    case noRefreshToken
}

// MARK: - Клиент

final class APIClient {
    private let session: URLSession
    private let tokens: TokenStorage
    
    init(session: URLSession = .shared, tokens: TokenStorage) {
        self.session = session
        self.tokens = tokens
    }
    
    // Регистрация + получение токенов
    func register(username: String, password: String) async throws -> AuthTokens {
        let url = APIConfig.baseURL.appendingPathComponent("/register")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let body: [String: String] = [
            "username": username,
            "password": password
        ]
        let timestamp = String(Int(Date().timeIntervalSince1970))
        let signature = generateSignature(username: username, password: password, timestamp: timestamp)
        
        request.addValue(timestamp, forHTTPHeaderField: "x_timestamp")
        request.addValue(signature, forHTTPHeaderField: "x_signature")
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(body)
        
        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse else { throw APIError.invalidResponse }
        guard (200..<300).contains(http.statusCode) else { throw APIError.http(http.statusCode) }
        
        let tokens = try JSONDecoder().decode(AuthTokens.self, from: data)
        self.tokens.save(tokens: tokens)
        return tokens
    }
    
    // Refresh
    func refreshTokens() async throws -> AuthTokens {
        guard let refresh = tokens.refreshToken else { throw APIError.noRefreshToken }
        let url = APIConfig.baseURL.appendingPathComponent("/refresh")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let bodyString = "refresh_token=\(refresh)"
        request.httpBody = bodyString.data(using: .utf8)
        
        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse else { throw APIError.invalidResponse }
        guard (200..<300).contains(http.statusCode) else { throw APIError.http(http.statusCode) }
        
        let tokens = try JSONDecoder().decode(AuthTokens.self, from: data)
        self.tokens.save(tokens: tokens)
        return tokens
    }
    
    // MARK: - Вспомогательные методы
    
    private func authorizedRequest(path: String,
                                   method: String = "GET") throws -> URLRequest {
        guard let access = tokens.accessToken else { throw APIError.invalidResponse }
        let url = APIConfig.baseURL.appendingPathComponent(path)
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.addValue(APIConfig.apiKey, forHTTPHeaderField: "X-API-KEY")
        request.addValue("Bearer \(access)", forHTTPHeaderField: "Authorization")
        return request
    }
    
    private func performWithRefresh<T: Decodable>(_ build: () throws -> URLRequest,
                                                  decodeTo: T.Type) async throws -> T {
        do {
            var request = try build()
            let (data, response) = try await session.data(for: request)
            if let http = response as? HTTPURLResponse, http.statusCode == 401 {
                // access токен протух — пробуем refresh
                let newTokens = try await refreshTokens()
                request.setValue("Bearer \(newTokens.access_token)", forHTTPHeaderField: "Authorization")
                let (data2, response2) = try await session.data(for: request)
                guard let http2 = response2 as? HTTPURLResponse else { throw APIError.invalidResponse }
                guard (200..<300).contains(http2.statusCode) else { throw APIError.http(http2.statusCode) }
                return try JSONDecoder().decode(T.self, from: data2)
            }
            guard let http = response as? HTTPURLResponse else { throw APIError.invalidResponse }
            guard (200..<300).contains(http.statusCode) else { throw APIError.http(http.statusCode) }
            return try JSONDecoder().decode(T.self, from: data)
        } catch {
            throw error
        }
    }
    
    // MARK: - Публичные методы под твой backend
    
    func getUserDateEnd(username: String) async throws -> String {
        let value: String = try await performWithRefresh({
            try authorizedRequest(path: "/get/\(username)/date")
        }, decodeTo: String.self)
        return value
    }
    
    func isUserSubbed(username: String) async throws -> Bool {
        let value: Bool = try await performWithRefresh({
            try authorizedRequest(path: "/is/\(username)/subbed")
        }, decodeTo: Bool.self)
        return value
    }
    
    func subscribe(username: String) async throws {
        // /subscribe — просто GET, без body
        let _: String = try await performWithRefresh({
            try authorizedRequest(path: "/subscribe")
        }, decodeTo: String.self)
    }
    
    func identify(username: String, imageData: Data, fileName: String = "image.jpg") async throws -> IdentifyResult {
        // multipart/form-data upload на /identify
        let boundary = "Boundary-\(UUID().uuidString)"
        var request = try authorizedRequest(path: "/identify")
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        body.appendString("--\(boundary)\r\n")
        body.appendString("Content-Disposition: form-data; name=\"image\"; filename=\"\(fileName)\"\r\n")
        body.appendString("Content-Type: image/jpeg\r\n\r\n")
        body.append(imageData)
        body.appendString("\r\n")
        body.appendString("--\(boundary)--\r\n")
        
        request.httpBody = body
        
        let result: IdentifyResult = try await performWithRefresh({ request }, decodeTo: IdentifyResult.self)
        return result
    }
}

// MARK: - Утилиты

extension Data {
    mutating func appendString(_ string: String) {
        if let d = string.data(using: .utf8) {
            append(d)
        }
    }
}

