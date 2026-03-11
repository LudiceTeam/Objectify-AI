import Foundation
import SwiftUI

@MainActor
final class AppViewModel: ObservableObject {
    @Published var username: String = ""
    @Published var password: String = ""
    @Published var isAuthorized: Bool = false
    
    @Published var endDate: String?
    @Published var isSubbed: Bool?
    @Published var identifyText: String?
    
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    private let tokens = TokenStorage()
    private lazy var api = APIClient(tokens: tokens)
    
    init() {
        isAuthorized = tokens.accessToken != nil
    }
    
    func register() async {
        isLoading = true
        errorMessage = nil
        do {
            _ = try await api.register(username: username, password: password)
            isAuthorized = true
            await loadUserInfo()
        } catch {
            errorMessage = "\(error)"
        }
        isLoading = false
    }
    
    func loadUserInfo() async {
        guard isAuthorized else { return }
        isLoading = true
        errorMessage = nil
        do {
            let date = try await api.getUserDateEnd(username: username)
            let sub = try await api.isUserSubbed(username: username)
            endDate = date
            isSubbed = sub
        } catch {
            errorMessage = "\(error)"
        }
        isLoading = false
    }
    
    func subscribe() async {
        isLoading = true
        errorMessage = nil
        do {
            try await api.subscribe(username: username)
            isSubbed = true
        } catch {
            errorMessage = "\(error)"
        }
        isLoading = false
    }
    
    func identify(imageData: Data) async {
        isLoading = true
        errorMessage = nil
        do {
            let res = try await api.identify(username: username, imageData: imageData)
            identifyText = res.result
        } catch {
            errorMessage = "\(error)"
        }
        isLoading = false
    }
    
    func logout() {
        tokens.clear()
        isAuthorized = false
        username = ""
        password = ""
        endDate = nil
        isSubbed = nil
        identifyText = nil
    }
}

