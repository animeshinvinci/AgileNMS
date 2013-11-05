from django import template


register = template.Library()


class StatusNameNode(template.Node):
    def __init__(self, check, status):
        self.check = template.Variable(check)
        self.status = template.Variable(status)

    def render(self, context):
        # Get check and status
        check = self.check.resolve(context)
        status = self.status.resolve(context)

        # If the check is disabled, print "disabled"
        if not check.enabled:
            return "disabled"

        # If the status is none, print "unknown"
        if status is None:
            return "unknown"

        # Print the status
        return status["status"]


@register.tag(name="status_name")
def do_status_name(parser, token):
    try:
        tag_name, check, status = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a two arguments" % token.contents.split()[0])
    return StatusNameNode(check, status)