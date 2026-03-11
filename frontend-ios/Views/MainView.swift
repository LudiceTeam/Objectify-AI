import SwiftUI

struct MainView: View {
    @EnvironmentObject var vm: AppViewModel
    @State private var showImagePicker = false
    @State private var pickedImageData: Data?
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    HStack {
                        Text("Hello, \(vm.username)")
                            .font(.title2.bold())
                        Spacer()
                        Button("Logout") {
                            vm.logout()
                        }
                        .foregroundColor(.red)
                    }
                    
                    GroupBox("Subscription") {
                        VStack(alignment: .leading, spacing: 8) {
                            if let date = vm.endDate {
                                Text("Trial / sub ends: \(date)")
                            }
                            if let subbed = vm.isSubbed {
                                Text("Subscribed: \(subbed ? "Yes" : "No")")
                            }
                            
                            HStack {
                                Button("Refresh status") {
                                    Task { await vm.loadUserInfo() }
                                }
                                
                                Button("Subscribe") {
                                    Task { await vm.subscribe() }
                                }
                                .buttonStyle(.borderedProminent)
                            }
                            .padding(.top, 4)
                        }
                    }
                    
                    GroupBox("Identify object") {
                        VStack(alignment: .leading, spacing: 12) {
                            Button("Pick image") {
                                showImagePicker = true
                            }
                            
                            if let text = vm.identifyText {
                                Text("Result: \(text)")
                            }
                        }
                    }
                    
                    if vm.isLoading {
                        ProgressView()
                            .frame(maxWidth: .infinity, alignment: .center)
                    }
                    
                    if let error = vm.errorMessage {
                        Text(error)
                            .foregroundColor(.red)
                    }
                }
                .padding()
            }
            .navigationTitle("Objectify AI")
        }
        .sheet(isPresented: $showImagePicker) {
            ImagePicker(data: $pickedImageData, onPicked: { data in
                if let d = data {
                    Task { await vm.identify(imageData: d) }
                }
            })
        }
        .task {
            if vm.endDate == nil || vm.isSubbed == nil {
                await vm.loadUserInfo()
            }
        }
    }
}

