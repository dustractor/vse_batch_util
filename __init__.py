bl_info = {
        "name": "batches",
        "blender": (2,80,0),
        "category":"util"
        }
import bpy,subprocess,pathlib,sys


def which(binary):
    use_what = ["which","where.exe"][sys.platform == "win32"]
    t = pathlib.Path(
            subprocess.run(
                [use_what,binary],
                capture_output=True
                ).stdout.decode().strip()
            ).resolve()
    if t.is_file():
        return str(t)


def batch(binary,cmd,inputdir,outputdir,glob_pat="*.png"):
    tcmd = cmd.split()
    for n,fpath in enumerate(pathlib.Path(inputdir).glob(glob_pat)):
        pad = "%04d" % n
        outname = str(pathlib.Path(outputdir) / (fpath.stem + pad + fpath.suffix))
        cmd = [binary,str(fpath),*tcmd,outname]
        print(cmd,end="-->")
        proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out,err = proc.communicate()
        if err:
            print("!",err)
        print("output: ",out)

def _(c=None,r=[]):
    if c:
        r.append(c)
        return c
    return r

@_
class BGT_UL_job_listitem(bpy.types.UIList):
    def draw_item(self,context,layout,data,item,icon,ac_data,ac_prop):
        layout.label(text=item.name)
        layout.label(text=item.binary)
        layout.label(text=item.cmd)
        layout.label(text=item.inputdir)
        layout.label(text=item.outputdir)


@_
class Job(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="batch")
    binary: bpy.props.StringProperty(
        subtype="FILE_PATH",
        default=which(["gmic","gmic.exe"][sys.platform=="win32"]))
    cmd: bpy.props.StringProperty(default="+norm +ge[-1] 30% +pixelsort[0] +,xy,[1],[2] output[3]")
    inputdir: bpy.props.StringProperty(subtype="DIR_PATH")
    outputdir : bpy.props.StringProperty(subtype="DIR_PATH")

@_
class Batches(bpy.types.PropertyGroup):
    jobs : bpy.props.CollectionProperty(type=Job)
    jobs_i : bpy.props.IntProperty(min=-1,default=-1)

@_
class BGT_OT_do_batch(bpy.types.Operator):
    bl_idname = "batches.do_batch"
    bl_label = "do batch"
    job_index: bpy.props.IntProperty()
    def execute(self,context):
        j = context.window_manager.batches.jobs[self.job_index]
        batch(j.binary,j.cmd,j.inputdir,j.outputdir)
        return {"FINISHED"}

@_
class BGT_OT_add_job(bpy.types.Operator):
    bl_idname = "batches.add_job"
    bl_label = "add job"
    def execute(self,context):
        batches = context.window_manager.batches
        new = batches.jobs.add()
        new.name = "foo"
        return {"FINISHED"}
@_
class BGT_PT_main_panel(bpy.types.Panel):
    bl_label = "batch"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "batch"
    @classmethod
    def poll(self,context):
        return any(list((s.type=="IMAGE" for s in context.selected_sequences)))
    def draw(self,context):
        b = context.window_manager.batches
        op = self.layout.operator("batches.do_batch")
        op.job_index = b.jobs_i
        j = b.jobs[b.jobs_i]
        self.layout.prop(j,"name")
        self.layout.prop(j,"binary")
        self.layout.prop(j,"cmd")
        self.layout.prop(j,"inputdir")
        self.layout.prop(j,"outputdir")
        for seq in context.selected_sequences:
            if seq.type == "IMAGE":
                self.layout.label(text=seq.name)
                self.layout.label(text=seq.directory)
                self.layout.label(text=str(len(seq.elements)))
                for elem in seq.elements:
                    print(elem.filename,elem.orig_width,elem.orig_height)
                print("dir(elem):",dir(elem))
                if hasattr(seq,"qdata"):
                    self.layout.label(text=seq.qdata)


@_
class BGT_PT_jobs(bpy.types.Panel):
    bl_label = "jobs"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "batch"
    bl_parent_id = "BGT_PT_main_panel"
    bl_order = 1
    def draw(self,context):
        wm = context.window_manager
        b = wm.batches
        self.layout.template_list("BGT_UL_job_listitem","",b,"jobs",b,"jobs_i")
        self.layout.operator("batches.add_job")


def register():
    list(map(bpy.utils.register_class,_()))
    bpy.types.Sequence.qdata = bpy.props.StringProperty()
    bpy.types.WindowManager.batches = bpy.props.PointerProperty(type=Batches)
    t = bpy.context.window_manager.batches.jobs.add()

def unregister():
    list(map(bpy.utils.unregister_class,_()))

