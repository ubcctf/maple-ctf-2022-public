use crate::utils;
use libc::{c_char, c_int, FILE};
use std::{ffi::CStr, mem};

extern "C" {
    static stdout: *mut FILE;
}

/// Hooks `puts`.
///
/// Passes call to `puts` in libc.
///
/// # Safety
///
/// Ensure that `s` is a valid C string.
#[no_mangle]
pub unsafe extern "C" fn puts(s: *const c_char) -> c_int {
    utils::log(
        format!(
            "puts(s=&\"{ptr_contents}\")\n",
            ptr_contents = CStr::from_ptr(s)
                .to_str()
                .expect("invalid string passed to puts"),
        )
        .as_str(),
    );

    let real_puts: extern "C" fn(*const c_char) -> c_int =
        mem::transmute(utils::dlsym_next("puts"));
    real_puts(s)
}

/// Hooks `fputs`.
///
/// Passes call to `fputs` in libc.
///
/// # Safety
///
/// Ensure that `s` is a valid C string.
#[no_mangle]
pub unsafe extern "C" fn fputs(s: *const c_char, stream: *mut FILE) -> c_int {
    utils::log(
        format!(
            "fputs(s=&\"{ptr_contents}\", stream={stream_fmt})\n",
            ptr_contents = CStr::from_ptr(s)
                .to_str()
                .expect("invalid string passed to fputs"),
            stream_fmt = if stream == stdout {
                "stdout"
            } else {
                "unknown"
            }
        )
        .as_str(),
    );

    let real_fputs: extern "C" fn(*const c_char, *mut FILE) -> c_int =
        mem::transmute(utils::dlsym_next("fputs"));
    real_fputs(s, stream)
}
