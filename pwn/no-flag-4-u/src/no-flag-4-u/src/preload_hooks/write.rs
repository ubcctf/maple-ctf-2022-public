use crate::utils;
use libc::{c_int, c_void, size_t, ssize_t, FILE};
use std::{mem, slice};

extern "C" {
    static stdout: *mut FILE;
}

/// Hooks `write`.
///
/// # Safety
///
/// Ensure that `buf` is at most `count` bytes.
#[no_mangle]
pub unsafe extern "C" fn write(fd: c_int, buf: *const c_void, count: size_t) -> ssize_t {
    utils::log(
        format!(
            "write(fd={fd}, buf=&\"{ptr_contents}\", count={count}\n",
            ptr_contents = if fd == 1 {
                String::from_utf8(slice::from_raw_parts::<u8>(buf as *const u8, count).to_vec())
                    .expect("invalid string passed to write")
            } else {
                String::from_utf8_lossy(slice::from_raw_parts::<u8>(buf as *const u8, count))
                    .to_string()
            },
        )
        .as_str(),
    );

    let real_write: extern "C" fn(c_int, *const c_void, size_t) -> ssize_t =
        mem::transmute(utils::dlsym_next("write"));
    real_write(fd, buf, count)
}

/// Hooks `fwrite`.
///
/// # Safety
///
/// Ensure that `ptr` has at most `n_items` of size `size`.
#[no_mangle]
pub unsafe extern "C" fn fwrite(
    ptr: *const c_void,
    size: size_t,
    n_items: size_t,
    stream: *mut FILE,
) -> size_t {
    if stream == stdout && size == 1 {
        utils::log(
            format!(
                "fwrite(ptr=&\"{ptr_contents}\", size={size}, n_items={n_items}), stream=stdout\n",
                ptr_contents = String::from_utf8(
                    slice::from_raw_parts::<u8>(ptr as *const u8, n_items).to_vec()
                )
                .expect("invalid string passed to fwrite")
            )
            .as_str(),
        );
    } else {
        utils::log(
            format!(
            "fwrite(ptr=&[{ptr_contents:x?}], size={size}, n_items={n_items}), stream={stream_fmt}\n",
            ptr_contents = slice::from_raw_parts::<u8>(ptr as *const u8, size * n_items),
            stream_fmt = if stream == stdout {
                "stdout"
            } else {
                "unknown"
            }
        )
            .as_str(),
        );
    }

    let real_fwrite: extern "C" fn(*const c_void, size_t, size_t, *mut FILE) -> size_t =
        mem::transmute(utils::dlsym_next("fwrite"));
    real_fwrite(ptr, size, n_items, stream)
}
