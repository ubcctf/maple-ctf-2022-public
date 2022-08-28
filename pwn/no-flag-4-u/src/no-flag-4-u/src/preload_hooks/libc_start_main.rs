use crate::{utils, MAIN_STARTED};
use libc::{c_char, c_int, exit};
use std::{mem, panic, sync::atomic::Ordering};

/// Hooks `__libc_start_main`.
///
/// - Sets `MAIN_STARTED` so other functions can switch to safe mode.
/// - Consumes 8 arguments in case glibc is compiled with `LIBC_START_MAIN_AUXVEC_ARG`.
/// - Calls `__libc_start_main` in glibc with the original arguments.
///
/// # Safety
///
/// This function should never be called directly.
/// The function is intended to be called by the linker when a program starts.
#[no_mangle]
unsafe extern "C" fn __libc_start_main(
    main: extern "C" fn(c_int, *const *const c_char, *const *const c_char) -> c_int,
    mut args: ...
) -> c_int {
    if cfg!(not(debug_assertions)) {
        panic::set_hook(Box::new(|_| {
            exit(-1);
        }));
    }

    panic::update_hook(move |prev, info| {
        utils::log(format!("{info}\n").as_str());
        prev(info);
    });

    MAIN_STARTED.store(true, Ordering::SeqCst);

    utils::init_log_stream();
    utils::log("Main Started\n");

    let real_libc_start_main: extern "C" fn(
        extern "C" fn(c_int, *const *const c_char, *const *const c_char) -> c_int,
        ...
    ) -> c_int = mem::transmute(utils::dlsym_next("__libc_start_main"));

    real_libc_start_main(
        main,
        args.arg::<usize>(),
        args.arg::<usize>(),
        args.arg::<usize>(),
        args.arg::<usize>(),
        args.arg::<usize>(),
        args.arg::<usize>(),
        args.arg::<usize>(),
    )
}
