import pkg_resources

def newrequest_streams():
    script = pkg_resources.resource_stream('solidproductionsystem', 'resources/newrequest.js')
    style = pkg_resources.resource_stream('solidproductionsystem', 'resources/newrequest.css')
    form = pkg_resources.resource_stream('solidproductionsystem', 'resources/newrequest_form.html')
    return script, style, form
