"""Run plant migration with deterministic ordering for symmetric alpha planes.
Keep actual z buffers and all pixel comparisons unchanged. Only the ordering key
for transparent face centers is rounded to 1e-9 model units (finer than the
independent directed-face check's 1e-7 resolution).
"""
import add_plants as plants

original_install = plants.install_template_support

def install_with_stable_alpha_order():
    original_install()
    path = plants.P / 'tools/audit_multiview.py'
    text = path.read_text()
    text = plants.replace_once(
        text,
        "fragments.append((float(p[:,2].mean()),region,depth,alpha,rgb,transparent))",
        "fragments.append((round(float(p[:,2].mean()),9),region,depth,alpha,rgb,transparent))"
    )
    path.write_text(text)

plants.install_template_support = install_with_stable_alpha_order
plants.main()
