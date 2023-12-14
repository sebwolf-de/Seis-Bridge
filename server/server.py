import jinja2
import misfits
import subprocess
import umbridge

class SeisSol(umbridge.Model):

    def __init__(self):
        print("Hello")
        self.name = "SeisSol"
        super().__init__("forward")

    def get_input_sizes(self, config):
        return [3]

    def get_output_sizes(self, config):
        return [5]

    def __call__(self, parameters, config):
        print(parameters)
        environment = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
        template = environment.get_template("fault_template.yaml")
        content = template.render(traction_left=parameters[0][0], traction_middle=parameters[0][1], traction_right=parameters[0][2])
        with open("fault_chain.yaml", "w+") as fault_file:
            fault_file.write(content)

        # Now start simulation
        subprocess.run(["rm", "-rf", "simulation"])
        subprocess.run(["mkdir", "simulation"])
        subprocess.run(["ls", "-la", "simulation"])
        subprocess.run(["mpirun", "--bind-to", "none", "-n", "4", "./launch.sh", "./SeisSol_Release_ssm_86_cuda_6_elastic", "parameters.par"])

        m = [-misfits.misfit("simulation", "reference", "tpv5", i)**2 for i in [1, 2, 3, 4, 5]]

        return [m]

    def supports_evaluate(self):
        return True

umbridge.serve_models([SeisSol()], 4244)
