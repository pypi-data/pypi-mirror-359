import argparse
import os
import humanize
import pwd
import datetime

parser = argparse.ArgumentParser()
parser.add_argument("path", help="Root directory to display")
parser.add_argument("--depth", type=int, default=-1, help="Max depth to traverse (-1 = unlimited)")
parser.add_argument("-e", type=str, default="", help="Only show files with specific extension eg : py , txt ")
parser.add_argument("-o", type=str, default="", help="Output to a specific file")
parser.add_argument("--show-hidden", action="store_true", help="Include hidden files")
parser.add_argument("--ztoa",action="store_true",help="View the tree in descending order.")
parser.add_argument("--meta",action="store_true",help="Add metadata to files.")

args = parser.parse_args()
dumpfile = None

def main():
    global dumpfile
    if args.o != "":
        dumpfile = open(args.o,"a")
    print_tree(args.path,max_depth= args.depth)
    if dumpfile != None:
        dumpfile.close()

def print_tree(path,prefix="",depth=0,max_depth=-1):
    
    
    if max_depth != -1 and depth > max_depth:
        return

    for i,entry in enumerate(sorted(os.listdir(path),reverse=True if args.ztoa else False)):
        if not args.show_hidden and entry[0] == '.':
            continue
        
        full_path = os.path.join(path,entry)
        connector = "└── " if i == len(os.listdir(path)) - 1 else "├── "

        if os.path.isdir(full_path):
            print(prefix+connector+f"📁 {entry}/",file=dumpfile)
            print_tree(full_path,prefix + ("    " if len(os.listdir(path))-1 == i else "|   "),depth+1,max_depth)
        else:
            if args.e != "" and str(entry).split('.')[-1] != args.e:
                continue
            try:
                size = os.path.getsize(full_path)
                size = humanize.naturalsize(size,binary=True)
            except:
                size = 0
            if args.meta:
                stats = os.stat(full_path)
                lm = datetime.datetime.fromtimestamp(stats.st_mtime)
                owner = pwd.getpwuid(stats.st_uid).pw_name
                print(prefix+connector+f"📄 {entry} [ {size} , Owner : {owner} , Last modified : {lm} ]",file=dumpfile)
            else:
                print(prefix+connector+f"📄 {entry} ({size})/",file=dumpfile)

if __name__ == "__main__":
    main()
