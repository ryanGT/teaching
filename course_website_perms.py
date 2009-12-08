#!/usr/bin/env python
import os, glob
import rwkos

def execute_w_echo(cmd):
    print(cmd)
    os.system(cmd)
               
def enable_one(pathin):
    cmd = 'chmod -R 755 '+ pathin
    execute_w_echo(cmd)

def enable_file(pathin):
    cmd = 'chmod 755 '+ pathin
    execute_w_echo(cmd)
    
def deny_one(pathin):
    cmd = 'chmod -R 700 '+ pathin
    execute_w_echo(cmd)
    
    
class website_dir(object):
    def __init__(self, root_path, enable_dirs, \
                 exclude_pats=['*exclude*']):
        self.root = root_path
        self.enable_dirs = enable_dirs
        self.exclude_pats = exclude_pats

    def deny_all(self):
        deny_one(self.root)

    def allow_dirs(self):
        for subdir in self.enable_dirs:
            curpath = os.path.join(self.root, subdir)
            if os.path.exists(curpath):
                enable_one(curpath)
            else:
                print('folder does not exist: ' + curpath)

    def enable_main(self):
        self.main_path = os.path.join(self.root, 'index.html')
        if os.path.exists(self.main_path):
            enable_file(self.main_path)
        else:
            print('main file does not exist: ' + self.main_path)

    def re_enable_root_dir(self):
        cmd = 'chmod 755 ' + self.root
        execute_w_echo(cmd)

    def find_excludes(self):
        self.exclude_folders = rwkos.glob_all_subdirs(cur_site.root, \
                                                      "*exclude*")

    def deny_excludes(self):
        for curfolder in self.exclude_folders:
            deny_one(curfolder)
            
    def run(self):
      self.deny_all()
      self.allow_dirs()
      self.enable_main()
      self.re_enable_root_dir()
      self.find_excludes()
      self.deny_excludes()
        
if __name__ == '__main__':
    classes = ['/home/ryan/siue/classes/mechatronics/2009']
    folders = ['lectures','outcomes','homework']
    for course in classes:
      cur_site = website_dir(course, folders)
      cur_site.run()
