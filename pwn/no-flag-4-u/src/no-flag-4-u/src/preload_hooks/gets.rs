use crate::utils;
use libc::{c_char, c_int, FILE};
use std::{ffi::CStr, mem};

extern "C" {
    static stdin: *mut FILE;
}

/// Hooks `gets`.
///
/// Passes call to `gets` in libc.
///
/// # Safety
///
/// Ensure that a valid string is read and the length is smaller than the size of the buffer.
#[no_mangle]
pub unsafe extern "C" fn gets(s: *mut c_char) -> *mut c_char {
    let (canary_addr, canary_value) = utils::get_bof_indicator(s as *const usize);

    let real_gets: extern "C" fn(*mut c_char) -> *mut c_char =
        mem::transmute(utils::dlsym_next("gets"));
    let result = real_gets(s);

    utils::log(
        format!(
            "gets(s=&\"{ptr_contents}\")\n",
            ptr_contents = CStr::from_ptr(s)
                .to_str()
                .expect("invalid string passed to gets"),
        )
        .as_str(),
    );

    if *canary_addr != canary_value {
        panic!("buffer overflow");
    }

    result
}

/// Hooks `fgets`.
///
/// Passes call to `fgets` in libc.
///
/// # Safety
///
/// Ensure that a valid string is read and that `n` is smaller than the size of the buffer.
#[no_mangle]
pub unsafe extern "C" fn fgets(s: *mut c_char, n: c_int, stream: *mut FILE) -> *mut c_char {
    let (canary_addr, canary_value) = utils::get_bof_indicator(s as *const usize);

    let real_fgets: extern "C" fn(*mut c_char, c_int, *mut FILE) -> *mut c_char =
        mem::transmute(utils::dlsym_next("fgets"));
    let result = real_fgets(s, n, stream);

    utils::log(
        format!(
            "fgets(s=&\"{ptr_contents}\", n={n} stream={stream_fmt})\n",
            ptr_contents = CStr::from_ptr(s)
                .to_str()
                .expect("invalid string passed to fgets"),
            stream_fmt = if stream == stdin { "stdin" } else { "unknown" }
        )
        .as_str(),
    );

    if *canary_addr != canary_value {
        panic!("buffer overflow");
    }

    result
}
