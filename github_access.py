
def init_app():
    def verif(params):
        if not isinstance(params.random_exercise, int):
            return False
        
        if isinstance(params.info, dict):
            for k,v in params.info.items():
                if not isinstance(k, str) or not isinstance(v, str):
                    return False
        else :
            return False
            
        if isinstance(params.all_exercises, list):
            if len(params.all_exercises) == 0:
                return False
            
            for el in params.all_exercises:
                if isinstance(el, dict):
                    if "name" not in el or "path_content" not in el or "type_page" not in el or "require" not in el:
                        return False
                    if not (isinstance(el["name"], str) and isinstance(el["path_content"], str) and isinstance(el["type_page"], str) and isinstance(el["require"], str)):
                        return False
                    if "path_code" in el and not isinstance(el["path_code"], str):
                        return False
                else :
                    return False
        else :
            return False
        
        return True
    
    def remove_trace():
        # delete all trace of the launch
        sys_modules = host_eval("new PyForeign(rte.sys_modules)")
        sys_modules.pop("github_access", None)
        globals().pop("github_access", None)
        sys_modules.pop("params", None)
        globals().pop("params", None)
        sys_modules.pop("launch", None)
        globals().pop("init_launch", None)
        sys_modules.pop("random", None)
        globals().pop("random", None)
        globals().pop("console", None)
        globals().pop("setTimeout", None)
        globals().pop("split_markdown", None)
        globals().pop("parse_front_matter", None)
        
        # delete all the file from the vm
        vm = \getCodeBootVM()
        vm.fs.deleteFile("launch.py")
        vm.fs.deleteFile("markdown.py")
        vm.fs.deleteFile("exercise.html")
        vm.fs.deleteFile("style.css")
        vm.fs.deleteFile("params.py")
        vm.fs.deleteFile("github_access.py")

        for ex in params.all_exercises:
            vm.fs.deleteFile(ex["name"] + '.md')
            if "path_code" in ex:
                vm.fs.deleteFile(ex["name"] + '.py')
    
    def custom_random_sample(seq, k):
        if k > len(seq):
            raise ValueError("Sample size cannot exceed population size.")
        
        seq = list(seq)  # make a copy to avoid modifying original
        result = []
        
        for idx, ex in enumerate(seq):
            if ex["require"] == "True":
                result.append((idx, ex))
                seq.pop(idx)
                
        for _ in range(k - len(result)):
            idx = random.randint(0, len(seq) - 1)
            result.append((idx, seq[idx]))
            seq.pop(idx)
        
        true_result = []
        for idx, ex in sorted(result, key=lambda x: x[0]):
            true_result.append(ex)
        return true_result
    
    # download the code from github
    write_file('launch.py', read_file('https://raw.githubusercontent.com/mael-charpentier/exercice_codeboot/refs/heads/codeboot/launch.py'))
    write_file('markdown.py', read_file('https://raw.githubusercontent.com/mael-charpentier/exercice_codeboot/refs/heads/codeboot/markdown.py'))
    write_file('exercise.html', read_file('https://raw.githubusercontent.com/mael-charpentier/exercice_codeboot/refs/heads/codeboot/exercise.html'))
    write_file('style.css', read_file('https://raw.githubusercontent.com/mael-charpentier/exercice_codeboot/refs/heads/codeboot/style.css'))
    write_file('params.py', read_file('https://raw.githubusercontent.com/mael-charpentier/exercice_codeboot/refs/heads/codeboot/params.py'))

    import params
    import random
    
    # verify params validity
    if not verif(params):
        return
    
    # download the code for all exercises from github
    for ex in params.all_exercises:
        write_file(ex["name"] + '.md', read_file(ex["path_content"]))
        if "path_code" in ex:
            write_file(ex["name"] + '.py', read_file(ex["path_code"]))

    # launch the app
    if params.random_exercise > 0:
        try:
            getSeedHash = host_eval("""
async (seedString) => {
    
    const encoder = new TextEncoder();
    const data = encoder.encode(seedString);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return BigInt('0x' + hashHex);
};
            """)
            
            def get_seed(seed_hash):
                random.seed(seed_hash)
                list_exo = custom_random_sample(params.all_exercises, params.random_exercise)
                from launch import init_launch
                init_launch(list_exo)
                remove_trace()
            
            already_try = False
            while True:
                student_number = prompt(("Error, try again.\n" if already_try else "") + "Number etudiant :") 
                if student_number in params.list_etudiant:
                    break
                already_try = True
            
            prompt_text = student_number
            for k,v in params.info.items():
                prompt_text += "_" + k + "_" + v
            
            getSeedHash(prompt_text).then(get_seed)
        except:
            remove_trace()
    else:
        try:
            from launch import init_launch
            init_launch(params.all_exercises)
        except:
            pass
        finally:
            remove_trace()

init_app()
globals().pop("init_app", None)