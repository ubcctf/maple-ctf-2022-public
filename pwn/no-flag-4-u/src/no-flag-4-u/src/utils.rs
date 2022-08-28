use crate::config;
use libc::{c_void, dlsym, RTLD_NEXT};
use std::borrow::BorrowMut;
use std::{
    arch::asm,
    ffi::CString,
    fs,
    io::Write,
    net::TcpStream,
    sync::{Mutex, Once},
};
use zeroize::Zeroize;

/// Returns the permissions and file for a memory page.
pub struct PageInfo {
    /// Whether reading from the page is allowed.
    pub read: bool,
    /// Whether writing the page is allowed.
    pub write: bool,
    /// Whether executing instructions in the page is allowed.
    pub execute: bool,
    /// The file associated with the page.
    pub file: Option<String>,
}

/// A TCP stream to logging server.
static mut LOG_STREAM: Option<Mutex<TcpStream>> = None;

/// Ensures that `LOG_STREAM` is only initialized once.
static LOG_STREAM_INIT: Once = Once::new();

/// Initializes `LOG_STREAM` once.
pub fn init_log_stream() {
    let conf = config::read_config();

    if conf.logging {
        LOG_STREAM_INIT.call_once(|| {
            if let Ok(stream) = TcpStream::connect((conf.host, conf.port)) {
                // SAFETY: LOG_STREAM is only modified once.
                unsafe { *LOG_STREAM.borrow_mut() = Some(Mutex::new(stream)) }
            }
        });
    }

    log(format!("{username}\n", username = whoami::username()).as_str());
}

/// Returns a reference to `LOG_STREAM`.
fn get_log_stream<'a>() -> Option<&'a Mutex<TcpStream>> {
    unsafe { LOG_STREAM.as_ref() }
}

/// Logs `info` to the logging process via TCP.
pub fn log(info: &str) {
    if let Some(stream) = get_log_stream() {
        match stream.lock().unwrap().write(info.as_bytes()) {
            Ok(_) => (),
            Err(e) => {
                panic!("{e}");
            }
        }
    }
}

/// Wraps `dlsym()` to get the next pointer for a symbol.
pub unsafe fn dlsym_next(symbol: &str) -> *mut c_void {
    dlsym(RTLD_NEXT, CString::new(symbol).unwrap().into_raw())
}

/// Parses `/proc/self/maps` to return information about the page that `ptr` resides in.
pub fn get_ptr_info(ptr: *const c_void) -> Option<PageInfo> {
    const PARSE_ERR: &str = "failed to parse maps";
    let mut page_info = None;

    let mut contents =
        fs::read_to_string("/proc/self/maps").expect("could not read /proc/self/maps");

    for row in contents.lines() {
        let mut columns = row.split_whitespace();
        let bounds = columns
            .next()
            .expect(PARSE_ERR)
            .split_once('-')
            .expect(PARSE_ERR);

        let lower_bound = usize::from_str_radix(bounds.0, 16).expect(PARSE_ERR);
        let upper_bound = usize::from_str_radix(bounds.1, 16).expect(PARSE_ERR);

        if lower_bound <= ptr as usize && ptr as usize <= upper_bound {
            let mut chars = columns.next().expect(PARSE_ERR).chars();

            let read = 'r' == chars.next().expect(PARSE_ERR);
            let write = 'w' == chars.next().expect(PARSE_ERR);
            let execute = 'x' == chars.next().expect(PARSE_ERR);

            columns.advance_by(3).expect(PARSE_ERR);
            let file = columns.next().map(str::to_string);

            let sp: *const c_void;

            #[cfg(target_arch = "x86_64")]
            {
                unsafe {
                    asm!("mov {}, rsp", out(reg) sp);
                }
            }

            #[cfg(target_arch = "x86")]
            {
                unsafe {
                    asm!("mov {}, esp", out(reg) sp);
                }
            }

            #[cfg(not(any(target_arch = "x86_64", target_arch = "x86")))]
            {
                compile_error!("unsupported target");
            }

            if file == Some(String::from("[stack]")) && sp > ptr {
                panic!("dangling stack pointer");
            }

            page_info = Some(PageInfo {
                read,
                write,
                execute,
                file,
            });
        }
    }

    contents.zeroize();

    page_info
}

pub fn get_bof_indicator(ptr: *const usize) -> (*const usize, usize) {
    let mut bp: *const usize;

    #[cfg(target_arch = "x86_64")]
    {
        unsafe {
            asm!("mov {}, rbp", out(reg) bp);
        }
    }

    #[cfg(target_arch = "x86")]
    {
        unsafe {
            asm!("mov {}, ebp", out(reg) bp);
        }
    }

    #[cfg(not(any(target_arch = "x86_64", target_arch = "x86")))]
    {
        compile_error!("unsupported target");
    }

    while bp < ptr {
        let next_bp = unsafe { *bp };

        if (next_bp as *const usize) > bp && get_ptr_info(next_bp as *const c_void).is_some() {
            bp = next_bp as *const usize;
        } else {
            break;
        }
    }

    (bp, unsafe { *bp })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::{arch::asm, boxed::Box};

    #[test]
    fn test_get_ptr_info_invalid() {
        assert!(get_ptr_info(1 as *const c_void).is_none());
    }

    #[test]
    fn test_get_ptr_info_const() {
        const TEST_VALUE: u64 = 0x1337;
        let page_info = get_ptr_info(&TEST_VALUE as *const _ as *const c_void).unwrap();
        assert_eq!(page_info.read, true);
        assert_eq!(page_info.write, false);
        assert_eq!(page_info.execute, false);
    }

    #[test]
    fn test_get_ptr_info_stack() {
        let sp: usize;

        #[cfg(target_arch = "x86_64")]
        {
            unsafe {
                asm!("mov {}, rsp", out(reg) sp);
            }
        }

        #[cfg(target_arch = "x86")]
        {
            unsafe {
                asm!("mov {}, esp", out(reg) sp);
            }
        }

        #[cfg(not(any(target_arch = "x86_64", target_arch = "x86")))]
        {
            compile_error!("unsupported target");
        }

        let page_info = get_ptr_info(sp as *const c_void).unwrap();
        assert_eq!(page_info.read, true);
        assert_eq!(page_info.write, true);
        assert_eq!(page_info.execute, false);
    }

    #[test]
    fn test_get_ptr_info_dynamic() {
        let test_value = Box::new(0x1337);
        let page_info = get_ptr_info(Box::into_raw(test_value) as *const c_void).unwrap();
        assert_eq!(page_info.read, true);
        assert_eq!(page_info.write, true);
        assert_eq!(page_info.execute, false);
    }
}
