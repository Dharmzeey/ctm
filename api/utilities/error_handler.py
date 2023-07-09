def render_errors(errors):
  """_summary_
    Renders the error messages from the serializer.errors dictionary.

  Args:
      errors (_type_): serializer.errors

  Returns:
      _type_: Dict[str, list]
  """
  error_messages = {}
  for field in errors:
    err = errors[field][0]
    error_messages[field] = [str(err)]
  return error_messages
