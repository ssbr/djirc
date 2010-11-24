import yaml
import jinja2

def guess_autoescape(_template_name):
    return True

class JinjaTemplateDict(object):
    def __init__(self, d):
        self.env = jinja2.Environment(
            autoescape=guess_autoescape,
            loader=jinja2.DictLoader(d),
            extensions=['jinja2.ext.autoescape'])
    
    @classmethod
    def from_yaml_f(cls, f):
        """Create a template dict from a file containing yaml with jinja2 values
        
        """
        return cls(yaml.safe_load(f))
    
    def __getitem__(self, k):
        return self.env.get_template(k)
