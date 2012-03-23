def setup_signals(progress_bar):
    import signal
    def progress(*args):
        print progress_bar
    for sig in (signal.SIGINFO, signal.SIGQUIT):
        signal.signal(sig, progress)
    print "Signal handlers installed:"
    print "Press Ctrl+T(BSD) / Ctrl+4(Linux) for progress"

