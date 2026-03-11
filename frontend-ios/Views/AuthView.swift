import SwiftUI

struct AuthView: View {
    @EnvironmentObject var vm: AppViewModel
    
    var body: some View {
        VStack(spacing: 24) {
            Text("Objectify AI")
                .font(.largeTitle.bold())
            
            TextField("Username", text: $vm.username)
                .textInputAutocapitalization(.none)
                .autocorrectionDisabled()
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(8)
            
            SecureField("Password (>= 8 символов)", text: $vm.password)
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(8)
            
            Button {
                Task { await vm.register() }
            } label: {
                if vm.isLoading {
                    ProgressView()
                } else {
                    Text("Register & Login")
                        .bold()
                        .frame(maxWidth: .infinity)
                }
            }
            .padding()
            .background(vm.isLoading || vm.username.isEmpty || vm.password.count < 8 ? Color.blue.opacity(0.5) : Color.blue)
            .foregroundColor(.white)
            .cornerRadius(10)
            .disabled(vm.username.isEmpty || vm.password.count < 8 || vm.isLoading)
            
            if let error = vm.errorMessage {
                Text(error)
                    .foregroundColor(.red)
                    .font(.footnote)
                    .multilineTextAlignment(.center)
            }
            
            Spacer()
        }
        .padding()
    }
}

