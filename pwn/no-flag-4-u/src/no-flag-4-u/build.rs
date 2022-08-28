use std::{env, path::PathBuf};

fn main() {
    // Path to the lib binary being tested.
    let mut test_lib_path = PathBuf::new();
    test_lib_path.push(env::var("CARGO_MANIFEST_DIR").unwrap());
    test_lib_path.push("target");
    test_lib_path.push(env::var("PROFILE").unwrap());
    test_lib_path.push("deps");
    test_lib_path
        .push("lib".to_owned() + &env::var("CARGO_PKG_NAME").unwrap().replace('-', "_") + ".so");

    // Sets the LD_PRELOAD environment variable for `inline-c` tests to load the lib.
    println!(
        "cargo:rustc-env=INLINE_C_RS_LD_PRELOAD={path}",
        path = test_lib_path.as_path().to_str().unwrap()
    );
}
