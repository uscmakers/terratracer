//
//  ContentView.swift
//  terratracer
//
//  Created by Kaylee on 2/10/25.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack(spacing: 20) {
            Text("TerraTracer")
                .font(.largeTitle)
                .fontWeight(.bold)
                .foregroundColor(.brown)

            Button(action: {
                print("Button Clicked!")
            }) {
                Text("Click Me")
                    .padding()
                    .background(Color.brown)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
        }
        .padding()
    }
}

// Preview for Xcode Canvas
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}

