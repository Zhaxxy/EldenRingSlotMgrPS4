from traceback import format_exc
try:
    import elden_ring_character_manager as ers
    import tkinter as tk
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import ttk
    from io import BytesIO
    import sys

    DELETE_NONE: dict = {'text':'Delete None','bg':'white','activebackground':'white'}
    REV_NONE: dict = {'text':'Resurrect None','bg':'white','activebackground':'white'}
    COPY_NONE: dict = {'text':'Copy None','bg':'white','activebackground':'white'}




    def save_same_file():
        global save_2_path
        global save_2_save

        if not root.title().startswith('*'):
            return False

        with open(save_2_path,'wb') as f:
            f.write(save_2_save.getvalue())

        unmark_save_2_as_changed()

    def ask_save():
        global save_2_path
        if messagebox.askyesno(title='Unsaved changes!',message=f'{save_2_path} has some unsaved changes\ndo you want to save?'):
            save_same_file()
        else:
            return

    def mark_save_2_as_changed():
        if root.title().startswith('*'):
            return
        text ='*' + save_2_name.cget('text')
        save_2_name.configure(text=text)
        root.title(text)

    def unmark_save_2_as_changed():
        if not root.title().startswith('*'):
            raise AssertionError('unmarking a save as unused, even though it is already')
        
        root.title(root.title()[1:])
        save_2_name.configure(text=save_2_name.cget('text')[1:])

    def save_1_tree_click(_: tk.Event = None):
        global save_1_copy_btn
        save1index = save_1_tree.curselection()
        save2index = save_2_tree.curselection()
        
        if not(save1index) or not(save2index):
            save_1_copy_btn.configure(**COPY_NONE)
            return

        if not ers.is_character_slot_in_use(save1index[0]+1,save_1_save):
            save_1_copy_btn.configure(**COPY_NONE)
            return        


        save_1_copy_btn.configure(text = f'Copy from {save_1_tree.get(save1index)}\n to {save_2_tree.get(save2index)}',bg='green',activebackground='green')

    root = tk.Tk()

    save_1_tree = tk.Listbox(root,exportselection=0)
    save_1_tree.grid(row=1,column=0)
    save_1_tree.bind("<ButtonRelease-1>", save_1_tree_click)


    save_1_name = tk.Label(root,text='Save 1')
    save_1_name.grid(row=0,column=0)


    def copy_command():
        if save_1_copy_btn.cget('text') == COPY_NONE['text']:
            return False
        save1index = save_1_tree.curselection()
        save2index = save_2_tree.curselection()
        
        if not(save1index) or not(save2index):
            raise AssertionError('wat')

        to_slot = save2index[0] + 1
        from_slot = save1index[0] + 1

        ers.copy_character_slot(from_slot,save_1_save,to_slot,save_2_save)

        update_save_1_tree()
        update_save_2_tree()
        mark_save_2_as_changed()


    save_1_copy_btn = tk.Button(root,**COPY_NONE,command=copy_command)
    save_1_copy_btn.grid(row=2,column=0)



    def save_2_tree_click(_: tk.Event = None):
        
        save2index = save_2_tree.curselection()
        if not save2index: return
        save_1_tree_click()
        slot_info = ers.get_character_slot_name(save2index[0]+1,save_2_save)

        if slot_info.name and not(slot_info.in_use):
            save_2_rev_btn.configure(text=f'Resurrect {save_2_tree.get(save2index)}',bg='green',activebackground='green')
        else:
            save_2_rev_btn.configure(**REV_NONE)
        
        if slot_info.in_use:
            save_2_delete_btn.configure(text=f'Delete {save_2_tree.get(save2index)}',bg='green',activebackground='green')
        else:
            save_2_delete_btn.configure(**DELETE_NONE)

    save_2_tree = tk.Listbox(root,exportselection=0)
    save_2_tree.grid(row=1,column=1)
    save_2_tree.bind("<ButtonRelease-1>", save_2_tree_click)

    save_2_name = tk.Label(root,text='Save 2')
    save_2_name.grid(row=0,column=1)

    def delete_command():
        if save_2_delete_btn.cget('text') == DELETE_NONE['text']:
            return False
        save2index = save_2_tree.curselection()
        
        if not save2index:
            raise AssertionError('wat')

        ers.delete_character_slot(save2index[0]+1,save_2_save)

        
        update_save_2_tree()
        mark_save_2_as_changed()

    save_2_delete_btn = tk.Button(root,**DELETE_NONE,command=delete_command)
    save_2_delete_btn.grid(row=2,column=1)


    def rev_command():
        if save_2_rev_btn.cget('text') == REV_NONE['text']:
            return False
        save2index = save_2_tree.curselection()
        
        if not save2index:
            raise AssertionError('wat')

        ers.resurrect_character_slot(save2index[0]+1,save_2_save)

        
        update_save_2_tree()
        mark_save_2_as_changed()


    save_2_rev_btn = tk.Button(root,**REV_NONE,command=rev_command)
    save_2_rev_btn.grid(row=3,column=1)


    menu = tk.Menu(root)
    root.config(menu=menu)

    def load_save_1():
        global save_1_path
        global save_1_save
        temp_save_1_path = filedialog.askopenfilename(title = 'Select your Elden Ring save!',filetypes = (('Decrypted Save', 'memory.dat'),('All files', '*.*')))
        try:
            with open(temp_save_1_path,'rb') as f:
                temp_save_1_save = BytesIO(f.read())
        except:
            return False

        try:
            ers.check_save(temp_save_1_save)
        except ers.InvalidEldenRingSavePS4 as e:
            messagebox.showerror(title='Invalid Save',message=f'{temp_save_1_path}\n{e}')
            return False
        
        save_1_name.configure(text=temp_save_1_path)

        save_1_path = temp_save_1_path
        save_1_save = temp_save_1_save
        update_save_1_tree()



    def update_save_1_tree():
        save_1_tree.selection_clear(0, tk.END)
        save_1_tree.delete(0, tk.END)
        save_1_tree_click()
        save_1_copy_btn.configure(**COPY_NONE)
        
        for slot_number in range(1,11):
            slot_info = ers.get_character_slot_name(slot_number,save_1_save)
            name = slot_info.name if slot_info.name else 'Empty'

            save_1_tree.insert(slot_number-1,f'{slot_number}: {name}')
            
            if not slot_info.in_use:
                save_1_tree.itemconfig(slot_number-1,{'bg':'red'})

    def load_save_2():
        global save_2_path
        global save_2_save

        if root.title().startswith('*'):
            ask_save()

        temp_save_2_path = filedialog.askopenfilename(title = 'Select your Elden Ring save!',filetypes = (('Decrypted Save', 'memory.dat'),('All files', '*.*')))
        try:
            with open(temp_save_2_path,'rb') as f:
                temp_save_2_save = BytesIO(f.read())
        except:
            return False

        try:
            ers.check_save(temp_save_2_save)
        except ers.InvalidEldenRingSavePS4 as e:
            messagebox.showerror(title='Invalid Save',message=f'{temp_save_2_path}\n{e}')
            return False

        save_2_name.configure(text=temp_save_2_path)
        root.title(temp_save_2_path)
        save_2_path = temp_save_2_path
        save_2_save = temp_save_2_save
        update_save_2_tree()


    def update_save_2_tree():
        save_2_tree.selection_clear(0, tk.END)
        save_2_tree.delete(0, tk.END)
        save_2_tree_click()
        save_2_rev_btn.configure(**REV_NONE)
        save_2_delete_btn.configure(**DELETE_NONE)
        for slot_number in range(1,11):
            slot_info = ers.get_character_slot_name(slot_number,save_2_save)
            name = slot_info.name if slot_info.name else 'Empty'

            save_2_tree.insert(slot_number-1,f'{slot_number}: {name}')
            
            if not slot_info.in_use:
                save_2_tree.itemconfig(slot_number-1,{'bg':'red'})



    filemenu1 = tk.Menu(menu)
    filemenu1.add_command(label='Load',command=load_save_1)


    menu.add_cascade(label="Save 1", menu=filemenu1)


    filemenu2 = tk.Menu(menu)
    filemenu2.add_command(label='Load',command=load_save_2)
    filemenu2.add_command(label='Save',command=save_same_file)
    filemenu2.add_command(label='COMING SOONG',)

    menu.add_cascade(label="Save 2", menu=filemenu2)
    root.iconbitmap('Icon.ico')
    root.protocol("WM_DELETE_WINDOW", lambda: (ask_save() if root.title().startswith('*') else None) or sys.exit())
    e
    root.mainloop()
except:
    messagebox.showerror(title='Something went wrong',message=f'{a}\nPlease report to Zhaxxy alongside any information and saves')
    