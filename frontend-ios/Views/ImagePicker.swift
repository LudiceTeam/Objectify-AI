import SwiftUI
import PhotosUI

struct ImagePicker: View {
    @Binding var data: Data?
    var onPicked: (Data?) -> Void
    
    @State private var selection: PhotosPickerItem?
    
    var body: some View {
        NavigationView {
            VStack {
                PhotosPicker(selection: $selection, matching: .images) {
                    Text("Choose image from gallery")
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
            }
            .navigationTitle("Select image")
            .onChange(of: selection) { newValue in
                guard let item = newValue else { return }
                Task {
                    if let data = try? await item.loadTransferable(type: Data.self) {
                        self.data = data
                        onPicked(data)
                    }
                }
            }
        }
    }
}

