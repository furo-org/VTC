import unreal

al=unreal.EditorAssetLibrary

PM_Mapping=[
  ("Material'/Game/KiteDemo/Environments/Foliage/BogMyrtle_01/BogMyrtle_01_Billboard_Mat.BogMyrtle_01_Billboard_Mat'",
  "PhysicalMaterial'/Game/Material/PM_Vegetation.PM_Vegetation'")
]

for assetRef,pmRef in PM_Mapping:
  a=al.load_asset(assetRef)
  if not a:
    print("fixup_assets.py: {} is not exist.".format(assetRef))
    continue
  pm=al.load_asset(pmRef)
  a.set_editor_property('phys_material',pm)
  print("Set phys_material {} on {}".format(pmRef, assetRef))
