import omni.ext
import omni.ui as ui
from .customdata_viewmodel import CustomDataAttributesModel

class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        
        self._usd_context = omni.usd.get_context()
        self._selection = self._usd_context.get_selection()
        self._events = self._usd_context.get_stage_event_stream()
        self._stage_event_sub = self._events.create_subscription_to_pop(
                        self._on_stage_event, name="customdataview"
                        )
        self._customdata_model = CustomDataAttributesModel()                        
        self._selected_primpath_model = ui.SimpleStringModel("-")        
        self._window = ui.Window("CustomData Properties", width=300, height=200)

        with self._window.frame:
            with ui.VStack():     
                ui.Label("selected prim:", height=20)        
                self._selectedPrimName = ui.StringField(model=self._selected_primpath_model, height=20, read_only=True)            

                ui.Label("custom properties:", height=20)        
                tree_view = ui.TreeView(
                    self._customdata_model,                    
                    root_visible=False,
                    header_visible=True,
                    columns_resizable=True,
                    column_widths=[ui.Fraction(0.4), ui.Fraction(0.6)],
                    style={"TreeView.Item": {"margin": 4}},
                )

    def _on_stage_event(self, event):
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self._on_selection_changed()

    def _on_selection_changed(self):
        
        selection = self._selection.get_selected_prim_paths()
        stage = self._usd_context.get_stage()
        print(f"== selection changed with {len(selection)} items")
        if selection and stage:
            #-- set last selected element in property model 
            if len(selection) > 0:
                path = selection[-1]
                self._selected_primpath_model.set_value(path )
                prim = stage.GetPrimAtPath(path) 
                self._customdata_model.set_prim(prim) 
            #-- print out all selected custom data 
            for selected_path in selection:
                print(f" item {selected_path}:")
                prim = stage.GetPrimAtPath(selected_path)
                for key in prim.GetCustomData():
                    print(f"   - {key} = {prim.GetCustomDataByKey(key)}")


    def on_shutdown(self):        
        # cleanup 
        self._window = None
        del self._stage_event_sub
        
