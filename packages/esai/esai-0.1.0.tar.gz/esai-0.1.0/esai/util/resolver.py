class Resolver:
    def __call__(self, path):
        parts = path.split(".")

        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)

        return m