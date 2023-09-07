{
  Exports all FormIDs from all loaded plugins, excluding Skyrim and Fallout 4 main game and DLC masters,
  along with the FULL / EDID / NAME field value, to a text file in the xEdit root folder.
  Written for xEdit (FO4Edit/TES5Edit).
}

unit UserScript;

var
  sl: TStringList;

procedure ExportFormIDs(e: IInterface);
var
  i: integer;
  PluginName, FormID: string;
  FULLValue, EDIDValue, NAMEValue: string;
begin
  // If the element is a main record, excluding plugin headers (TES4 records).
  if (ElementType(e) = etMainRecord) and (Signature(e) <> 'TES4') then
  begin
    PluginName := GetFileName(GetFile(e));
    FormID := IntToHex(FixedFormID(e), 8);
    FULLValue := GetElementEditValues(e, 'FULL');
    EDIDValue := GetElementEditValues(e, 'EDID');
    NAMEValue := GetElementEditValues(e, 'NAME');
    if FULLValue <> '' then
      FormID := PluginName + ' | ' + FormID + ' | ' + FULLValue
    else if EDIDValue <> '' then
      FormID := PluginName + ' | ' + FormID + ' | ' + EDIDValue
	else if NAMEValue <> '' then
      FormID := PluginName + ' | ' + FormID + ' | ' + NAMEValue
    else
      FormID := PluginName + ' | ' + FormID + ' | ' + '[CHECK MANUALLY WITH XEDIT]';
    sl.Add(FormID);
  end
  else if ElementType(e) = etGroupRecord then
  begin
    // Iterate through group elements and process them recursively.
    for i := 0 to ElementCount(e) - 1 do
      ExportFormIDs(ElementByIndex(e, i));
  end;
end;

function Initialize: integer;
var
  PluginName: string;
  i,j: Integer;
  plugin: IInterface;
  e: IInterface;
begin
  // Create and initialize string list to store FormIDs + FULL / EDID / NAME.
  sl := TStringList.Create;
  sl.Sorted := True;
  sl.Duplicates := dupIgnore;

  for i := 0 to FileCount - 1 do begin
    plugin := FileByIndex(i);
    PluginName := GetFileName(plugin);
    AddMessage('Grabbing FormIDs From: ' + PluginName + '...');
    
    if SameText(PluginName, 'Skyrim.esm') or
       SameText(PluginName, 'TESV.exe') or
       SameText(PluginName, 'SkyrimSE.exe') or
       SameText(PluginName, 'Update.esm') or
       SameText(PluginName, 'Dawnguard.esm') or
       SameText(PluginName, 'HearthFires.esm') or
       SameText(PluginName, 'Dragonborn.esm') or
       SameText(PluginName, 'Fallout4.esm') or
       SameText(PluginName, 'Fallout4.exe') or
       SameText(PluginName, 'DLCRobot.esm') or
       SameText(PluginName, 'DLCworkshop01.esm') or
       SameText(PluginName, 'DLCCoast.esm') or
       SameText(PluginName, 'DLCworkshop02.esm') or
       SameText(PluginName, 'DLCworkshop03.esm') or
       SameText(PluginName, 'DLCNukaWorld.esm') then
      Continue;

    for j := 0 to Pred(RecordCount(plugin)) do begin
      e := RecordByIndex(plugin, j);
      ExportFormIDs(e);
    end;
  end;
end;

function Finalize: integer;
var
  dlgSave: TSaveDialog;
  FileName: string;
begin
  // Set output file name and save FormIDs + FULL / EDID / NAME values to the file.

  if sl.Count > 1 then begin
    // ask for file to export to
    dlgSave := TSaveDialog.Create(nil);
    dlgSave.Options := dlgSave.Options + [ofOverwritePrompt];
    dlgSave.Filter := 'Text files (*.txt)|*.txt';
    dlgSave.InitialDir := ProgramPath;
    dlgSave.FileName := 'Plugins_FormIDs.txt';
    if dlgSave.Execute then
    begin
      sl.SaveToFile(dlgSave.FileName);
      AddMessage('FormIDs and their values have been exported to: ' + dlgSave.FileName);
    end
    else
        AddMessage('Save aborted.');
    dlgSave.Free;
  end
  else
    AddMessage('Nothing to export.');


  // Free the string list and display a message.
  sl.Free;
end;

end.
