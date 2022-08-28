mod libc_start_main;

#[cfg(not(feature = "disable_read_hooks"))]
pub mod read;

#[cfg(not(feature = "disable_write_hooks"))]
pub mod write;

#[cfg(not(feature = "disable_gets_hooks"))]
pub mod gets;

#[cfg(not(feature = "disable_puts_hooks"))]
pub mod puts;

#[cfg(not(feature = "disable_scanf_hooks"))]
pub mod scanf;

#[cfg(not(feature = "disable_printf_hooks"))]
pub mod printf;

#[cfg(not(feature = "disable_heap_hooks"))]
pub mod heap;
