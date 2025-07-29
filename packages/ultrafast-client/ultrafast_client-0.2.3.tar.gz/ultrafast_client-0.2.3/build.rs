fn main() {
    // PyO3 0.25+ handles configuration automatically
    // We only need to handle macOS-specific linking

    // Handle macOS Python symbol linking
    // On macOS, Python extension modules need undefined dynamic lookup
    if cfg!(target_os = "macos") {
        println!("cargo:rustc-link-arg=-undefined");
        println!("cargo:rustc-link-arg=dynamic_lookup");
    }
}
