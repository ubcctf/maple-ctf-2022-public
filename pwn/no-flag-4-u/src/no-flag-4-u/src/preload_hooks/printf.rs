use crate::utils;
use libc::{c_char, c_int, c_void, size_t, FILE};
use std::{
    ffi::{CStr, VaList},
    mem, panic,
};

/// The risk level from parsing a format string.
#[derive(Debug, PartialEq, Eq)]
enum FormatStringResult {
    /// No extra mitigations necessary.
    LowRisk,
    /// Format string is non-constant and should be changed for safety.
    NonConstant,
}

extern "C" {
    static stdout: *mut FILE;
}

/// Constant for a `"%s\0"` format string.
const PERCENT_S: *const c_char = "%s\0".as_ptr() as *const c_char;

/// If the format string is non-constant, replace with a safe version.
/// Calls `vfprintf` in glibc with potentially modified arguments to mitigate security risks.
///
/// # Safety
///
/// This function should only be called by other hooked `printf` functions.
unsafe fn vfprintf_internal(stream: *mut FILE, format: *const c_char, ap: VaList) -> c_int {
    match check_format_string(format) {
        FormatStringResult::LowRisk => {
            let real_vfprintf: extern "C" fn(*mut FILE, *const c_char, VaList) -> c_int =
                mem::transmute(utils::dlsym_next("vfprintf"));
            real_vfprintf(stream, format, ap)
        }
        FormatStringResult::NonConstant => {
            let real_fprintf: extern "C" fn(*mut FILE, *const c_char, ...) -> c_int =
                mem::transmute(utils::dlsym_next("fprintf"));
            real_fprintf(stream, PERCENT_S, format)
        }
    }
}

/// Hooks `vfprintf`.
///
/// Passes call to `vfprintf_internal`.
///
/// # Safety
///
/// Do not allow arbitrary format strings.
/// Ensure that the arguments agree with the format string directives.
///
/// See `man "printf(3)"` for more details.
#[no_mangle]
pub unsafe extern "C" fn vfprintf(stream: *mut FILE, format: *const c_char, ap: VaList) -> c_int {
    utils::log(
        format!(
            "vfprintf(format=&\"{ptr_contents}\")\n",
            ptr_contents = CStr::from_ptr(format)
                .to_str()
                .expect("invalid format string"),
        )
        .as_str(),
    );
    vfprintf_internal(stream, format, ap)
}

/// Hooks `vprintf`.
///
/// Passes call to `vfprintf_internal`.
///
/// # Safety
///
/// Do not allow arbitrary format strings.
/// Ensure that the arguments agree with the format string directives.
///
/// See `man "printf(3)"` for more details.
#[no_mangle]
pub unsafe extern "C" fn vprintf(format: *const c_char, ap: VaList) -> c_int {
    utils::log(
        format!(
            "vprintf(format=&\"{ptr_contents}\")\n",
            ptr_contents = CStr::from_ptr(format)
                .to_str()
                .expect("invalid format string"),
        )
        .as_str(),
    );
    vfprintf_internal(stdout, format, ap)
}

/// Hooks `printf`.
///
/// Passes call to `vfprintf_internal`.
///
/// # Safety
///
/// Do not allow arbitrary format strings.
/// Ensure that the arguments agree with the format string directives.
///
/// See `man "printf(3)"` for more details.
#[no_mangle]
pub unsafe extern "C" fn fprintf(stream: *mut FILE, format: *const c_char, mut args: ...) -> c_int {
    utils::log(
        format!(
            "fprintf(format=&\"{ptr_contents}\")\n",
            ptr_contents = CStr::from_ptr(format)
                .to_str()
                .expect("invalid format string"),
        )
        .as_str(),
    );
    vfprintf_internal(stream, format, args.as_va_list())
}

/// Hooks `printf`.
///
/// Passes call to `vprintf_internal`.
///
/// # Safety
///
/// Do not allow arbitrary format strings.
/// Ensure that the arguments agree with the format string directives.
///
/// See `man "printf(3)"` for more details.
#[no_mangle]
pub unsafe extern "C" fn printf(format: *const c_char, mut args: ...) -> c_int {
    utils::log(
        format!(
            "printf(format=&\"{ptr_contents}\")\n",
            ptr_contents = CStr::from_ptr(format)
                .to_str()
                .expect("invalid format string"),
        )
        .as_str(),
    );
    vfprintf_internal(stdout, format, args.as_va_list())
}

/// If the format string is non-constant, replace with a safe version.
/// Calls `vdprintf` in glibc with potentially modified arguments to mitigate security risks.
///
/// # Safety
///
/// This function should only be called by other hooked `dprintf` functions.
unsafe fn vdprintf_internal(fd: c_int, format: *const c_char, ap: VaList) -> c_int {
    match check_format_string(format) {
        FormatStringResult::LowRisk => {
            let real_vdprintf: extern "C" fn(c_int, *const c_char, VaList) -> c_int =
                mem::transmute(utils::dlsym_next("vdprintf"));
            real_vdprintf(fd, format, ap)
        }
        FormatStringResult::NonConstant => {
            let real_dprintf: extern "C" fn(c_int, *const c_char, ...) -> c_int =
                mem::transmute(utils::dlsym_next("dprintf"));
            real_dprintf(fd, PERCENT_S, format)
        }
    }
}

/// Hooks `vdprintf`.
///
/// Passes call to `vdprintf_internal`.
///
/// # Safety
///
/// Do not allow arbitrary format strings.
/// Ensure that the arguments agree with the format string directives.
///
/// See `man "printf(3)"` for more details.
#[no_mangle]
pub unsafe extern "C" fn vdprintf(fd: c_int, format: *const c_char, ap: VaList) -> c_int {
    utils::log(
        format!(
            "vdprintf(format=&\"{ptr_contents}\")\n",
            ptr_contents = CStr::from_ptr(format)
                .to_str()
                .expect("invalid format string"),
        )
        .as_str(),
    );
    vdprintf_internal(fd, format, ap)
}

/// Hooks `dprintf`.
///
/// Passes call to `vdprintf_internal`.
///
/// # Safety
///
/// Do not allow arbitrary format strings.
/// Ensure that the arguments agree with the format string directives.
///
/// See `man "printf(3)"` for more details.
#[no_mangle]
pub unsafe extern "C" fn dprintf(fd: c_int, format: *const c_char, mut args: ...) -> c_int {
    utils::log(
        format!(
            "dprintf(format=&\"{ptr_contents}\")\n",
            ptr_contents = CStr::from_ptr(format)
                .to_str()
                .expect("invalid format string"),
        )
        .as_str(),
    );
    vdprintf_internal(fd, format, args.as_va_list())
}

/// If the format string is non-constant, replace with a safe version.
/// Calls `vsprintf` in glibc with potentially modified arguments to mitigate security risks.
///
/// # Safety
///
/// This function should only be called by other hooked `snprintf` functions.
unsafe fn vsnprintf_internal(
    s: *mut c_char,
    size: size_t,
    format: *const c_char,
    ap: VaList,
) -> c_int {
    match check_format_string(format) {
        FormatStringResult::LowRisk => {
            let real_vsnprintf: extern "C" fn(*mut c_char, size_t, *const c_char, VaList) -> c_int =
                mem::transmute(utils::dlsym_next("vsnprintf"));
            real_vsnprintf(s, size, format, ap)
        }
        FormatStringResult::NonConstant => {
            let real_snprintf: extern "C" fn(*mut c_char, size_t, *const c_char, ...) -> c_int =
                mem::transmute(utils::dlsym_next("snprintf"));
            real_snprintf(s, size, PERCENT_S, format)
        }
    }
}

/// Hooks `vsnprintf`.
///
/// Passes call to `vsnprintf_internal`.
///
/// # Safety
///
/// Do not allow arbitrary format strings.
/// Ensure that the arguments agree with the format string directives.
/// Ensure that `size` is less than the size of the buffer.
///
/// See `man "printf(3)"` for more details.
#[no_mangle]
pub unsafe extern "C" fn vsnprintf(
    s: *mut c_char,
    size: size_t,
    format: *const c_char,
    ap: VaList,
) -> c_int {
    utils::log(
        format!(
            "vsnprintf(format=&\"{ptr_contents}\")\n",
            ptr_contents = CStr::from_ptr(format)
                .to_str()
                .expect("invalid format string"),
        )
        .as_str(),
    );
    vsnprintf_internal(s, size, format, ap)
}

/// Hooks `snprintf`.
///
/// Passes call to `vsnprintf_internal`.
///
/// # Safety
///
/// Do not allow arbitrary format strings.
/// Ensure that the arguments agree with the format string directives.
/// Ensure that `size` is less than the size of the buffer.
///
/// See `man "printf(3)"` for more details.
#[no_mangle]
pub unsafe extern "C" fn snprintf(
    s: *mut c_char,
    size: size_t,
    format: *const c_char,
    mut args: ...
) -> c_int {
    utils::log(
        format!(
            "snprintf(format=&\"{ptr_contents}\")\n",
            ptr_contents = CStr::from_ptr(format)
                .to_str()
                .expect("invalid format string"),
        )
        .as_str(),
    );
    vsnprintf(s, size, format, args.as_va_list())
}

/// If the format string is non-constant, replace with a safe version.
/// Calls `vsprintf` in glibc potentially with modified arguments to mitigate security risks.
///
/// # Safety
///
/// This function should only be called by other hooked `sprintf` functions.
unsafe extern "C" fn vsprintf_internal(
    s: *mut c_char,
    format: *const c_char,
    ap: VaList,
) -> c_int {
    match check_format_string(format) {
        FormatStringResult::LowRisk => {
            let real_vsprintf: extern "C" fn(*mut c_char, *const c_char, VaList) -> c_int =
                mem::transmute(utils::dlsym_next("vsprintf"));
            real_vsprintf(s, format, ap)
        }
        FormatStringResult::NonConstant => {
            let real_sprintf: extern "C" fn(*mut c_char, *const c_char, ...) -> c_int =
                mem::transmute(utils::dlsym_next("sprintf"));
            real_sprintf(s, PERCENT_S)
        }
    }
}

/// Hooks `vsprintf`.
///
/// passes call to `vsprintf_internal`.
///
/// # Safety
///
/// Do not allow arbitrary format strings.
/// Ensure that the arguments agree with the format string directives.
/// Ensure that the length of the output will never exceed the size of the buffer.
///
/// See `man "printf(3)"` for more details.
#[no_mangle]
pub unsafe extern "C" fn vsprintf(s: *mut c_char, format: *const c_char, ap: VaList) -> c_int {
    utils::log(
        format!(
            "vsprintf(format=&\"{ptr_contents}\")\n",
            ptr_contents = CStr::from_ptr(format)
                .to_str()
                .expect("invalid format string"),
        )
        .as_str(),
    );
    vsprintf_internal(s, format, ap)
}

/// Hooks `sprintf`.
///
/// passes call to `vsprintf_internal`.
///
/// # Safety
///
/// Do not allow arbitrary format strings.
/// Ensure that the arguments agree with the format string directives.
/// Ensure that the length of the output will never exceed the size of the buffer.
///
/// See `man "printf(3)"` for more details.
#[no_mangle]
pub unsafe extern "C" fn sprintf(s: *mut c_char, format: *const c_char, mut args: ...) -> c_int {
    utils::log(
        format!(
            "sprintf(format=&\"{ptr_contents}\")\n",
            ptr_contents = CStr::from_ptr(format)
                .to_str()
                .expect("invalid format string"),
        )
        .as_str(),
    );
    vsprintf(s, format, args.as_va_list())
}

/// Performs sanity checks on the format string specified by `format`.
///
/// - Returns `FormatStringResult::LowRisk` if everything passes.
/// - Returns `FormatStringResult::NonConstant` if non-constant.
/// - Panics if format string is dangerous.
fn check_format_string(format: *const c_char) -> FormatStringResult {
    let page_info =
        utils::get_ptr_info(format as *const c_void).expect("invalid format string pointer");

    if page_info.execute || !page_info.read {
        panic!("invalid format string permissions");
    }

    if page_info.file == Some(String::from("[stack]"))
        || page_info.file == Some(String::from("[heap]"))
        || page_info.write
    {
        return FormatStringResult::NonConstant;
    }

    if cfg!(feature = "enable_restrict_n_directive") {
        let s = unsafe { CStr::from_ptr(format) }
            .to_str()
            .expect("invalid format string");

        let mut directive_in_progress = false;

        for c in s.chars() {
            if directive_in_progress {
                match c {
                    'n' => panic!("dangerous conversion specifier prohibited"),
                    '*' | '.' | '$' => (), // field width, precision, '$'
                    '#' | '0' | '-' | ' ' | '+' | '\'' | 'I' => (), // flags
                    'h' | 'l' | 'q' | 'L' | 'j' | 'z' | 'Z' | 't' => (), // length modifier
                    d if d.is_ascii_digit() => (),
                    _ => directive_in_progress = false,
                }
            } else if c == '%' {
                directive_in_progress = true;
            }
        }
    }

    FormatStringResult::LowRisk
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::ffi::CString;

    #[test]
    #[should_panic]
    fn test_check_format_string_null() {
        _ = panic::take_hook();
        check_format_string(0 as *const c_char);
    }

    #[test]
    fn test_normal() {
        assert_eq!(
            check_format_string("%d %s Test String!\0".as_ptr() as *const c_char),
            FormatStringResult::LowRisk
        );
    }

    #[test]
    fn test_nonconstant() {
        assert_eq!(
            check_format_string(
                CString::new("%d %s Test String!").unwrap().into_raw() as *const c_char
            ),
            FormatStringResult::NonConstant
        );
    }

    #[test]
    #[cfg_attr(feature = "enable_restrict_n_directive", should_panic)]
    fn test_check_basic_n_directive() {
        _ = panic::take_hook();
        check_format_string("%n\0".as_ptr() as *const c_char);
    }

    #[test]
    #[cfg_attr(feature = "enable_restrict_n_directive", should_panic)]
    fn test_check_complex_n_directive() {
        _ = panic::take_hook();
        check_format_string("%1$hhn\0".as_ptr() as *const c_char);
    }
}
