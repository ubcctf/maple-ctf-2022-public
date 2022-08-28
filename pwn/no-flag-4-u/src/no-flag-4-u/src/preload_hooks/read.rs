use crate::utils;
use libc::{c_int, c_void, size_t, ssize_t, FILE};
use std::{mem, slice};

extern "C" {
    static stdin: *mut FILE;
}

/// Hooks `read`.
///
/// # Safety
///
/// Ensure that `buf` has enough capacity to fit `count` bytes.
#[no_mangle]
pub unsafe extern "C" fn read(fd: c_int, buf: *mut c_void, count: size_t) -> ssize_t {
    let (canary_addr, canary_value) = utils::get_bof_indicator(buf as *const usize);

    let real_read: extern "C" fn(c_int, *mut c_void, size_t) -> ssize_t =
        mem::transmute(utils::dlsym_next("read"));
    let result = real_read(fd, buf, count);

    if fd == 0 {
        utils::log(
            format!(
                "read(fd={fd}, buf=&\"{ptr_contents}\", count={count}\n",
                ptr_contents = if fd == 0 {
                    String::from_utf8(
                        slice::from_raw_parts::<u8>(buf as *const u8, result as usize).to_vec(),
                    )
                    .expect("invalid string passed to read")
                } else {
                    String::from_utf8_lossy(slice::from_raw_parts::<u8>(
                        buf as *const u8,
                        result as usize,
                    ))
                    .to_string()
                },
            )
            .as_str(),
        );
    }

    if *canary_addr != canary_value {
        panic!("buffer overflow");
    }

    result
}

/// Hooks `fread`.
///
/// # Safety
///
/// Ensure that `ptr` has enough capacity to fit `n_items` of size `size`.
#[no_mangle]
pub unsafe extern "C" fn fread(
    ptr: *mut c_void,
    size: size_t,
    n_items: size_t,
    stream: *mut FILE,
) -> size_t {
    let (canary_addr, canary_value) = utils::get_bof_indicator(ptr as *const usize);

    let real_fread: extern "C" fn(*mut c_void, size_t, size_t, *mut FILE) -> size_t =
        mem::transmute(utils::dlsym_next("fread"));
    let result = real_fread(ptr, size, n_items, stream);

    if stream == stdin && size == 1 {
        utils::log(
            format!(
                "fread(ptr=&\"{ptr_contents}\", size=1, n_items={n_items}), stream=stdin\n",
                ptr_contents = String::from_utf8(
                    slice::from_raw_parts::<u8>(ptr as *const u8, result).to_vec()
                )
                .expect("invalid string passed to fread")
            )
            .as_str(),
        );
    } else {
        utils::log(
            format!(
            "fread(ptr=&[{ptr_contents:x?}], size={size}, n_items={n_items}), stream={stream_fmt}\n",
            ptr_contents = slice::from_raw_parts::<u8>(ptr as *const u8, size * n_items),
            stream_fmt = if stream == stdin {
                "stdin"
            } else {
                "unknown"
            }
        )
            .as_str(),
        );
    }

    if *canary_addr != canary_value {
        panic!("buffer overflow");
    }

    result
}
