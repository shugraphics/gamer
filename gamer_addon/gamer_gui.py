# This branch was created to work on the tetrahedralization.

import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
    FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, \
    PointerProperty, StringProperty, BoolVectorProperty
import mathutils
import gamer

# python imports
import os
import numpy as np


# we use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


def panel_select_callback (self, context):
    self.panel_select_callback(context)


class GAMER_OT_coarse_dense(bpy.types.Operator):
    bl_idname = "gamer.coarse_dense"
    bl_label = "Coarse Dense"
    bl_description = "Decimate selected dense areas of the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.gamer.mesh_improve_panel.coarse_dense(context)
        return {'FINISHED'}


class GAMER_OT_coarse_flat(bpy.types.Operator):
    bl_idname = "gamer.coarse_flat"
    bl_label = "Coarse Flat"
    bl_description = "Decimate selected flat areas of the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.gamer.mesh_improve_panel.coarse_flat(context)
        return {'FINISHED'}


class GAMER_OT_smooth(bpy.types.Operator):
    bl_idname = "gamer.smooth"
    bl_label = "Smooth"
    bl_description = "Smooth selected vertices of the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.gamer.mesh_improve_panel.smooth(context)
        return {'FINISHED'}


class GAMER_OT_normal_smooth(bpy.types.Operator):
    bl_idname = "gamer.normal_smooth"
    bl_label = "Normal Smooth"
    bl_description = "Smooth facet normals of selected faces of the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.gamer.mesh_improve_panel.normal_smooth(context)
        return {'FINISHED'}


class GAMerMeshImprovementPropertyGroup(bpy.types.PropertyGroup):
  dense_rate = FloatProperty(
      name="CD_Rate", default=2.5, min=0.001, max=4.0, precision=4,
      description="The rate for coarsening dense areas")
  dense_iter = IntProperty(
      name="CD_Iter", default=1, min=1, max=15,
      description="The number of iterations for coarsening dense areas")
  flat_rate = FloatProperty(
      name="CF_Rate", default=0.016, min=0.00001, max=0.5, precision=4,
      description="The rate for coarsening flat areas")
  max_min_angle = IntProperty(
      name="Max_Min_Angle", default=15, min=10, max=20,
      description="The maximal minumum angle for smoothing")
  smooth_iter = IntProperty(
      name="S_Iter", default=6, min=1, max=50,
      description="The number of iterations for coarsening dense areas")
  preserve_ridges = BoolProperty( name="Preserve ridges", default=False)
  new_mesh = BoolProperty( name="Create new mesh", default=False)

  def coarse_dense ( self, context):
      print("Calling coarse_dense")
      gmesh, boundaries = blender_to_gamer(create_new_mesh=self.new_mesh)
      gmesh.coarse_dense(rate=self.dense_rate, numiter=self.dense_iter)
      gamer_to_blender(gmesh, boundaries, create_new_mesh=self.new_mesh)

  def coarse_flat ( self, context):
      print("Calling coarse_flat")
      gmesh, boundaries = blender_to_gamer(create_new_mesh=self.new_mesh)
      gmesh.coarse_flat(rate=self.flat_rate)
      gamer_to_blender(gmesh, boundaries, create_new_mesh=self.new_mesh)

  def smooth ( self, context):
      print("Calling smooth")
      gmesh, boundaries = blender_to_gamer(create_new_mesh=self.new_mesh)
      gmesh.smooth(max_min_angle=self.max_min_angle, max_iter=self.smooth_iter, preserve_ridges=self.preserve_ridges)
      gamer_to_blender(gmesh, boundaries, create_new_mesh=self.new_mesh)

  def normal_smooth ( self, context):
      print("Calling smooth")
      gmesh, boundaries = blender_to_gamer(create_new_mesh=self.new_mesh)
      gmesh.normal_smooth()
      gamer_to_blender(gmesh, boundaries, create_new_mesh=self.new_mesh)

  def draw_layout ( self, context, layout ):
      row = layout.row()
      col = row.column()
      col.operator("gamer.coarse_dense",icon="OUTLINER_OB_LATTICE")
      col = row.column()
      col.prop(self, "dense_rate" )
      col = row.column()
      col.prop(self, "dense_iter" )

      row = layout.row()
      col = row.column()
      col.operator("gamer.coarse_flat",icon="OUTLINER_OB_LATTICE")
      col = row.column()
      col.prop(self, "flat_rate" )

      row = layout.row()
      col = row.column()
      col.operator("gamer.smooth",icon="OUTLINER_OB_LATTICE")
      col = row.column()
      col.prop(self, "max_min_angle" )
      col = row.column()
      col.prop(self, "smooth_iter" )

      row = layout.row()
      row.prop(self, "preserve_ridges" )

      row = layout.row()
      col = row.column()
      col.operator("gamer.normal_smooth",icon="OUTLINER_OB_LATTICE")

      row = layout.row()
      row.prop(self, "new_mesh" )


  def draw_panel ( self, context, panel ):
      layout = panel.layout
      self.draw_layout ( context, layout )



# Tetrahedralization Operators:

class GAMER_OT_tet_domain_add(bpy.types.Operator):
    bl_idname = "gamer.tet_domain_add"
    bl_label = "Add a Tet Domain"
    bl_description = "Add a new tetrahedralization domain"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.gamer.tet_group.add_tet_domain(context)
        return {'FINISHED'}

class GAMER_OT_tet_domain_remove(bpy.types.Operator):
    bl_idname = "gamer.tet_domain_remove"
    bl_label = "Remove a Tet Domain"
    bl_description = "Remove a tetrahedralization domain"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.gamer.tet_group.remove_active_tet_domain(context)
        self.report({'INFO'}, "Deleted Active Tet Group")
        return {'FINISHED'}


class GAMER_OT_generic_button(bpy.types.Operator):
    bl_idname = "gamer.generic_button"
    bl_label = "Generic Button"
    bl_description = ("Generic Button")
    bl_options = {'REGISTER'}

    def execute(self, context):
        print ( "Executed" )
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


class GAMerTetDomainPropertyGroup(bpy.types.PropertyGroup):
    # name = StringProperty()  # This is a reminder that "name" is already defined for all subclasses of PropertyGroup
    domain_id = IntProperty ( name="ID", default=-1, description="Domain ID" )
    marker = IntProperty ( name="Marker", default=-1, description="Domain Marker Integer" )
    is_hole = BoolProperty ( name="Hole", default=False, description="Use this domain as a hole" )
    constrain_vol  = BoolProperty ( name="Constrain Volume", default=False, description="Constrain Volume" )
    vol_constraint = FloatProperty ( name="Vol Constraint", default=10.0, description="Volume Constraint" )

    min_dihedral = FloatProperty ( name="Min Dihedral", default=10.0, description="Minimum Dihedral in Degrees" )
    max_aspect_ratio = FloatProperty ( name="Max Aspect Ration", default=1.3, description="Maximum Aspect Ratio" )

    dolfin = BoolProperty ( name="DOLFIN", default=False, description="DOLFIN" )
    diffpack = BoolProperty ( name="Diffpack", default=False, description="Diffpack" )
    carp = BoolProperty ( name="Carp", default=False, description="Carp" )
    fetk = BoolProperty ( name="FEtk", default=False, description="FEtk" )
    ho_mesh = BoolProperty ( name="Higher order mesh generation", default=False, description="Higher order mesh generation" )
    
    def draw_layout ( self, layout ):

        row = layout.row()
        col = row.column()
        col.prop ( self, "marker" )
        col = row.column()
        col.prop ( self, "is_hole" )

        row = layout.row()
        col = row.column()
        col.prop ( self, "constrain_vol" )
        if self.constrain_vol:
            col = row.column()
            col.prop ( self, "vol_constraint" )

        row = layout.row()
        col = row.column()
        col.prop ( self, "min_dihedral" )
        col = row.column()
        col.prop ( self, "max_aspect_ratio" )
        
        row = layout.row()
        col = row.column()
        col.prop ( self, "dolfin" )
        col = row.column()
        col.prop ( self, "diffpack" )

        row = layout.row()
        col = row.column()
        col.prop ( self, "carp" )
        col = row.column()
        col.prop ( self, "fetk" )

        row = layout.row()
        col = row.column()
        col.operator ( "gamer.generic_button", text="Tetrahedralize" )
        col = row.column()
        col.prop ( self, "ho_mesh" )


class GAMer_UL_domain(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # The draw_item function is called for each item of the collection that is visible in the list.
        #   data is the RNA object containing the collection,
        #   item is the current drawn item of the collection,
        #   icon is the "computed" icon for the item (as an integer, because some objects like materials or textures
        #        have custom icons ID, which are not available as enum items).
        #   active_data is the RNA object containing the active property for the collection (i.e. integer pointing to the
        #        active item of the collection).
        #   active_propname is the name of the active property (use 'getattr(active_data, active_propname)').
        #   index is index of the current item in the collection.
        #   flt_flag is the result of the filtering process for this item.
        #   Note: as index and flt_flag are optional arguments, you do not have to use/declare them here if you don't
        #         need them.

        tet = item

        row = layout.row()
        col = row.column()
        col.label ( "Domain ID: " + str(tet.domain_id) )
        col = row.column()
        col.label ( "Domain Marker: " + str(tet.marker) )


class GAMerTetrahedralizationPropertyGroup(bpy.types.PropertyGroup):

  generic_float = FloatProperty( name="Generic Float", default=123.456, min=0.0, max=1000, precision=4, description="A Generic Float Value")
  generic_int = IntProperty( name="Generic Int", default=5, min=1, max=10, description="A Generic Int Value")
  generic_boolean = BoolProperty( name="Generic Bool", default=False, description="A Generic Boolean Value")

  domain_list = CollectionProperty(type=GAMerTetDomainPropertyGroup, name="Domain List")
  active_domain_index = IntProperty(name="Active Domain Index", default=0)
  next_id = IntProperty(name="Counter for Unique Domain IDs", default=1)  # Start ID's at 1 to confirm initialization

  def draw_layout ( self, context, layout ):

      row = layout.row()
      col = row.column()

      col.template_list("GAMer_UL_domain", "",
                        self, "domain_list",
                        self, "active_domain_index",
                        rows=2)

      col = row.column(align=True)
      col.operator("gamer.tet_domain_add", icon='ZOOMIN', text="")
      col.operator("gamer.tet_domain_remove", icon='ZOOMOUT', text="")

      if len(self.domain_list) > 0:
          domain = self.domain_list[self.active_domain_index]

          row = layout.row()
          row.label ( "Active Index = " + str ( self.active_domain_index ) + ", ID = " + str ( domain.domain_id ) )
          
          domain.draw_layout ( layout )

  def add_tet_domain ( self, context):
      print("Adding a Tet Domain")
      """ Add a new tet domain to the list of tet domains and set as the active domain """
      new_dom = self.domain_list.add()
      new_dom.domain_id = self.allocate_available_id()
      self.active_domain_index = len(self.domain_list)-1

  def remove_active_tet_domain ( self, context):
      print("Removing active Tet Domain")
      """ Remove the active tet domain from the list of domains """
      self.domain_list.remove ( self.active_domain_index )
      self.active_domain_index -= 1
      if self.active_domain_index < 0:
          self.active_domain_index = 0
          print ( "That was the last one!!!" )

  def allocate_available_id ( self ):
      """ Return a unique domain ID for a new domain """
      print ( "Next ID is " + str(self.next_id) )
      if len(self.domain_list) <= 0:
          # Reset the ID to 1 when there are no more molecules
          self.next_id = 1
      self.next_id += 1
      return ( self.next_id - 1 )

  def draw_panel ( self, context, panel ):
      layout = panel.layout
      self.draw_layout ( context, layout )



class GAMerMainPanelPropertyGroup(bpy.types.PropertyGroup):
    mesh_improve_select = BoolProperty ( name="mesh_improve_sel", description="Surface Mesh Improvement", default=False, subtype='NONE', update=panel_select_callback)
    tet_select = BoolProperty ( name="tet_sel", description="Tetrahedralization", default=False, subtype='NONE', update=panel_select_callback)
    select_multiple = BoolProperty ( name="select_multiple", description="Show Multiple Panels", default=False, subtype='NONE', update=panel_select_callback)
    last_state = BoolVectorProperty ( size=22 ) # Keeps track of previous button state to detect transitions

    def panel_select_callback ( self, context ):
        """
        Desired Logic:
          pin_state 0->1 with no others selected:
            Show All
          pin_state 0->1 with just 1 selected:
            No Change (continue showing the currently selected, and allow more)
          pin_state 0->1 with more than 1 selected ... should NOT happen because only one panel should show when pin_state is 0
            Illegal state
          pin_state 1->0 :
            Hide all panels ... always
        """

        prop_keys = [ 'mesh_improve_select', 'tet_select', 'select_multiple' ]

        pin_state = False

        if self.get('select_multiple'):
            pin_state = (self['select_multiple'] != 0)
        old_pin_state = (self.last_state[prop_keys.index('select_multiple')] != 0)

        if (old_pin_state and (not pin_state)):
            # Pin has been removed, so hide all panels ... always
            # print ("Hiding all")
            for k in prop_keys:
                self.last_state[prop_keys.index(k)] = False
                self[k] = 0
            self.last_state[prop_keys.index('select_multiple')] = False

        elif ((not old_pin_state) and pin_state):
            # Pin has been pushed
            # Find out how many panels are currently shown
            num_panels_shown = 0
            for k in prop_keys:
                if k != 'select_multiple':
                    if self.get(k):
                        if self[k] != 0:
                            num_panels_shown += 1
            # Check for case where no panels are showing
            if num_panels_shown == 0:
                # print ("Showing all")
                # Show all panels
                for k in prop_keys:
                    if self.get(k):
                        self[k] = 1
                        self.last_state[prop_keys.index(k)] = False

            self.last_state[prop_keys.index('select_multiple')] = True

        else:
            # Pin state has not changed, so assume some other button has been toggled

            # Go through and find which one has changed to positive, setting all others to 0 if not pin_state
            for k in prop_keys:
                if self.get(k):
                    if (self[k] != 0) and (self.last_state[prop_keys.index(k)] == False):
                        self.last_state[prop_keys.index(k)] = True
                    else:
                        if not pin_state:
                            self.last_state[prop_keys.index(k)] = False
                            self[k] = 0


    def draw_self(self, context, layout):

        # Draw the panel selection buttons with labels:

        brow = layout.row()
        bcol = brow.column()
        bcol.prop ( self, "mesh_improve_select", icon='MESH_ICOSPHERE', text="Surface Mesh Improvement" )
        bcol = brow.column()
        bcol.prop ( self, "tet_select", icon='MESH_CONE', text="Tetrahedralization" )
        bcol = brow.column()

        if self.select_multiple:
            bcol.prop ( self, "select_multiple", icon='PINNED', text="Show All / Multiple" )
        else:
            bcol.prop ( self, "select_multiple", icon='UNPINNED', text="Show All / Multiple" )

        # Draw each panel only if it is selected

        if self.mesh_improve_select:
            layout.box() # Use as a separator
            layout.label ( "Surface Mesh Improvement", icon='MESH_ICOSPHERE' )
            context.scene.gamer.mesh_improve_panel.draw_layout ( context, layout )

        if self.tet_select:
            layout.box() # Use as a separator
            layout.label ( "Tetrahedralization", icon='MESH_CONE' )
            context.scene.gamer.tet_group.draw_layout ( context, layout )



class GAMER_PT_main_panel(bpy.types.Panel):
    bl_label = "GAMer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "GAMer"
   
    @classmethod
    def poll(cls, context):
        return (context.scene is not None)

    '''
    def draw_header(self, context):
        # LOOK HERE!! This is where the icon is actually included in the panel layout!
        # The icon() method takes the image data-block in and returns an integer that
        # gets passed to the 'icon_value' argument of your label/prop constructor or
        # within a UIList subclass
        img = bpy.data.images.get('cellblender_icon')
        #could load multiple images and animate the icon too.
        #icons = [img for img in bpy.data.images if hasattr(img, "icon")]
        if img is not None:
            icon = self.layout.icon(img)
            self.layout.label(text="", icon_value=icon)
    '''

    def draw(self, context):
        context.scene.gamer.main_panel.draw_self(context,self.layout)


class GAMerPropertyGroup(bpy.types.PropertyGroup):
  initialized = BoolProperty(name="GAMer Initialized", default=False)
  gamer_version = StringProperty(name="GAMer Version", default="0")

  main_panel = PointerProperty(
    type=GAMerMainPanelPropertyGroup,
    name="GAMer Main Panel")

  mesh_improve_panel = PointerProperty(
    type=GAMerMeshImprovementPropertyGroup,
    name="GAMer Surface Mesh Improvement")

  tet_group = PointerProperty(
    type=GAMerTetrahedralizationPropertyGroup,
    name="GAMer Tetrahedralization")

  def init_properties ( self ):
    self.gamer_version = "0.1"
    self.initialized = True



def setObjectMode(obj):
    editmode = obj.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    return editmode


def setEditMode(obj):
    editmode = obj.mode
    bpy.ops.object.mode_set(mode='EDIT')
    return editmode


def restoreInteractionMode(obj,editmode):
    bpy.ops.object.mode_set(mode=editmode)


def vertToVec(v):
    return[v[0],v[1],v[2]]


def vertFromVec(v):
    return mathutils.Vector((v[0],v[1],v[2]))


def toggle(var,val):
    var = val


def getSelectedMesh(errorreport=True):
    "Returns the selected mesh"
    objs = bpy.context.selected_objects
    obj = objs[0] if len(objs) else None
    # myprint(obj)
    if not obj or obj.type != 'MESH':
        if errorreport:
#            self.drawError(errormsg="expected a selected mesh")
            print("expected a selected mesh") 
        return None
    return obj



def getMeshVertices(obj, selected=False):
    mesh = obj.data
    if selected:
        vert_indices = [v.index for v in mesh.vertices if v.select and not v.hide]
        vertices = [vertToVec(mesh.vertices[vi].co) for vi in vert_indices]
        return vertices, vert_indices
    else:
        vertices = [vertToVec(v.co) for v in mesh.vertices]
        return vertices
    

def getMeshFaces( obj, selected = False):
    mesh = obj.data
    if selected :
        mfaces_indices = [face.index for face in mesh.polygons
                         if face.select and not face.hide]
        faces = [mesh.polygons[fi].vertices for fi in mfaces_indices]
        return faces, mfaces_indices
    else :
        faces = [f.vertices for f in mesh.polygons]
        return faces


def getTranslation(obj):
    return obj.location#("worldspace")#[obj.LocX,obj.LocY,obj.LocZ]#obj.matrixWorld[3][0:3]


def getBoundaryFaces(self, boundary):
    if not "faces" in boundary:
        return []
    all_faces = []
    for faces in list(boundary["faces"].values()):
        all_faces.extend(faces)

    return all_faces


def setBoundaryFaces(boundary, faces):
    "Set faces in boundary props"
    if not "faces" in boundary:
        return
    # Maximal indices in a array prop in Blender is 10000
    max_ind = 10000
    num_sub_arrays = int(len(faces)/max_ind)+1

    # If the faces allready exist delete it and re attach it
    if "faces" in boundary:
        for key in boundary["faces"]:
            del boundary["faces"][key]
        del boundary["faces"]

    boundary["faces"] = {}
    for ind in range(num_sub_arrays):
        boundary["faces"]["F%d"%ind] = faces[ind*max_ind: \
                                             min((ind+1)*max_ind, len(faces))]



def createMesh(mesh_name, verts, faces, smooth=False, color=[0.8,0.8,0.8]):

    mesh = bpy.data.meshes.new(mesh_name)

    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.calc_normals()

    return mesh



def blender_to_gamer(obj=None, create_new_mesh=False, check_for_vertex_selection=True):
    "Transfer the active mesh to a GAMer surface mesh"
    # Take the first one
    #myprint("blender_to_gamer ", obj)

    
    # Get selected mesh
    if obj is None:
        obj = getSelectedMesh()
    #myprint("blender_to_gamer getSelectedMesh ", obj.name)
    if obj is None:
        return None, None

    # Ensure editmode is off
    editmode = setObjectMode(obj)

#    self.waitingCursor(1)
    
    # Grab vertices and Faces
    vertices, selected_vertices = getMeshVertices(obj, selected=True)
    vertices = getMeshVertices(obj)
    faces = getMeshFaces(obj)

    # myprint("verts ",len(vertices), len(faces))
    # Get world location and offset each vertex with this value
    if create_new_mesh:
        translation = getTranslation(obj)
    else:
        translation = [0., 0., 0.]
        
    # Init gamer mesh
    gmesh = gamer.SurfaceMesh(len(vertices), len(faces))
    def setVert(co, gvert, sel):
        gvert.x = co[0] + translation[0]
        gvert.y = co[1] + translation[1]
        gvert.z = co[2] + translation[2]
        gvert.sel = bool(sel)

    # Check we have vertices selected
    if check_for_vertex_selection and not selected_vertices:
        myprint("No selected vertices")
        return None, None
    
    # If all vertices are selected
    if len(selected_vertices) == len(vertices):
        selected_vertices = np.ones(len(vertices), dtype=bool)
    else:
        selection = np.zeros(len(vertices), dtype=bool)
        selection[selected_vertices] = 1
        selected_vertices = selection
    
    [setVert(*args) for args in zip(vertices, gmesh.vertices(), selected_vertices)]

    # Transfere data from blender mesh to gamer mesh
    for face, gface in zip(faces, gmesh.faces()):
        if len(face) != 3:
#            self.drawError(errormsg="expected mesh with only triangles in")
            print("expected a triangulated mesh")
#            self.waitingCursor(0)
            restoreInteractionMode(obj,editmode)
            return None, None
        
        gface.a, gface.b, gface.c = face
        gface.m = -1

    # Transfer boundary information
    boundaries = obj.get('boundaries')
    if not boundaries:
        obj['boundaries'] = {}
        boundaries = obj['boundaries']

    # Iterate over the faces and transfer marker information
    for boundary in boundaries.values():
        for face_ind in getBoundaryFaces(boundary):
            gmesh.face(face_ind).m = boundary["marker"]

#    self.waitingCursor(0)
    #myprint(gmesh)
    # Restore editmode
    restoreInteractionMode(obj,editmode)
    return gmesh, boundaries



def gamer_to_blender(gmesh, boundaries, create_new_mesh=False,
                     mesh_name="gamer_improved", switch_layer=True):
    #myprint("gamer_to_blender ",gmesh)
    # Check arguments
    if not isinstance(gmesh, gamer.SurfaceMesh):
#        self.drawError(errormsg="expected a GAMer SurfaceMesh") 
        print("expected a SurfaceMesh") 
    
    # Get scene
    scn = bpy.context.scene
#    self.waitingCursor(1)
    
    verts = [(gvert.x, gvert.y, gvert.z) for gvert in gmesh.vertices()]
    un_selected_vertices = [i for i, gvert in enumerate(gmesh.vertices())
                            if not gvert.sel]
    
    faces = [(gface.a, gface.b, gface.c) for gface in gmesh.faces()]
    markers = [(i, gface.m) for i, gface in enumerate(gmesh.faces()) \
               if gface.m != -1]

    # If we create a new mesh we copy the boundaries to a dict
    if create_new_mesh:
        new_boundaries = {}
        for boundary_name in boundaries.keys():
            boundary = boundaries[boundary_name]
            new_boundaries[boundary_name] = dict(
                marker=boundary["marker"], r=boundary["r"], g=boundary["g"], \
                b=boundary["b"], faces={})
        
        # Do not copy the faces information grab that from the gamer mesh
        boundaries = new_boundaries
    
    # Create marker to boundary map
    face_markers = {}
    for boundary in boundaries.values():
        face_markers[boundary["marker"]] = []

    # Gather all faces of a marker
    for face, marker in markers:
        if marker in face_markers:
            face_markers[marker].append(face)

    # Set the faces of the corresponding boundary
    for boundary in boundaries.values():
        setBoundaryFaces(boundary, face_markers[boundary["marker"]])
    
    # Ensure editmode is off
    obj = getSelectedMesh()
    editmode = setObjectMode(obj)

    if create_new_mesh:

        # Create new object and mesh
        bmesh = createMesh(mesh_name, verts, faces, smooth=False, color=[0.8,0.8,0.8])
        obj = bpy.data.objects.new(mesh_name, bmesh)
        scn.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT')
        obj.select=True
    
        # If not generating a totally new mesh
        switch_to_layer = self.helper.getLayers(scn)[-1]
        if switch_layer:
            # Switch to another layer
            # Assumes Blenders 20 layer framework...
            switch_to_layer += 1
            switch_to_layer = 1 if switch_to_layer > 20 else switch_to_layer

        self.helper.setLayers(scn, [switch_to_layer])
        self.helper.setLayers(obj, [switch_to_layer])
        
        self.helper.addObjectToScene(scn, obj)
        self.helper.ObjectsSelection([obj])

        # Set the property dictionary
        # FIXME: Is this safe? Is boundaries always something I can use?
#        self.helper.setProperty(obj, "boundaries", boundaries)
        obj['boundaries'] = boundaries
    
    else:

        orig_mesh = obj.data
        bmesh = createMesh('gamer_tmp', verts, faces, smooth=False, color=[0.8,0.8,0.8])
        obj.data = bmesh
        bpy.data.meshes.remove(orig_mesh)
        bmesh.name = mesh_name

    #myprint("un_selected_vertices ", len(un_selected_vertices))
    [toggle(v.select,False) for v in bmesh.vertices if v.index in un_selected_vertices]
    
    # Restore editmode
    restoreInteractionMode(obj,editmode)

    # Repaint boundaries if there were markers in the GAMer data
# FIXME:
#    if markers:
#        self._repaint_boundaries(obj)
    
#    self.waitingCursor(0)
#    self.updateViewer()

