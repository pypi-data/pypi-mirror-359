"""
Tool To Generate nerd Icons Classes

Copyright (c) 2025 Obito. All Rights Reserved.

nerdicons_gen path/to/gen 


"""
import requests,json,io,sys
# fetch Into A .temp_file 
def fetch_data():
    res = requests.get("https://github.com/ryanoasis/nerd-fonts/raw/refs/heads/master/glyphnames.json")
    with open(".temp_icons_map.json","wb") as f:
        f.write(res.content)
def get_perfix(key):
    return key.split("-")[0]
def Gen(path):
    buffers = {}
    with open(".temp_icons_map.json","r") as f:
        data = json.loads(f.read())
    for key,value in data.items():
        if key == "METADATA":
            continue
        perfix = get_perfix(key)
        class_name = perfix.capitalize()
        if perfix not in buffers:
            buffers[perfix] = io.StringIO()

            buffers[perfix].write(f"# This File GEN using nerdicons_gen.py\n\nclass {class_name}:\n")

        buffers[perfix].write(f"\n\t# CHAR : {value['char']}\n\t{key.replace('-','_')} = \"\\u{value['code']}\"")
    for perfix,buffer in buffers.items():
        with open(f"{path}{perfix}.py","w") as f:
            f.write(buffer.getvalue())
def main():
    args = sys.argv
    if len(args) == 1:
        print("unValid Usage \nput --help for help")
    elif len(args) > 1:
        if args[1] == "--help":
            print("Usage:\n\nnerdicons_gen path/to/ \n")
        else:
            Gen(sys.argv[1])
if __name__=="__main__":
    main()
