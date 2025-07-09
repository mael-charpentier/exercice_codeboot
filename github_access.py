
def init_app():
    # download the code from github
    write_file('launch.py', read_file(''))
    write_file('markdown.py', read_file(''))
    write_file('exercise.html', read_file(''))
    write_file('style.css', read_file(''))
    write_file('params.py', read_file(''))

    import params

    for ex in params.all_exercises:
        write_file(ex["name"] + '.md', read_file(ex["path"]))

    # run the code
    from launch import launch_init
    t = launch_init(params)

    sys_modules = host_eval("new PyForeign(rte.sys_modules)")
    sys_modules.pop("github_access", None)
    globals().pop("github_access", None)
    sys_modules.pop("params", None)
    globals().pop("params", None)
    sys_modules.pop("launch", None)
    globals().pop("launch_init", None)
    globals().pop("console", None)
    globals().pop("setTimeout", None)
    globals().pop("split_markdown", None)
    globals().pop("parse_front_matter", None)
    
    
    vm = \getCodeBootVM()
    vm.fs.deleteFile("launch.py")
    vm.fs.deleteFile("markdown.py")
    vm.fs.deleteFile("exercise.html")
    vm.fs.deleteFile("style.css")
    vm.fs.deleteFile("params.py")
    vm.fs.deleteFile("github_access.py")

    for ex in params.all_exercises:
        vm.fs.deleteFile(ex["name"] + '.md')
    
    return t

__exercise_final_utils__ = init_app()
globals().pop("init_app", None)