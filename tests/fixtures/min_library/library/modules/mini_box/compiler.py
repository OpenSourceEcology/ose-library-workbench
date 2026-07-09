def compile(schema, doc):
    obj = doc.addObject("Part::Box", schema["nested"]["label"])
    obj.Width = schema["width_in"]
    obj.Enabled = schema["nested"]["enabled"]
    return [obj]
