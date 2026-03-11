import SwiftUI

@main
struct ObjectifyAIApp: App {
    @StateObject private var viewModel = AppViewModel()
    
    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(viewModel)
        }
    }
}

struct RootView: View {
    @EnvironmentObject var vm: AppViewModel
    
    var body: some View {
        Group {
            if vm.isAuthorized {
                MainView()
            } else {
                AuthView()
            }
        }
    }
}

