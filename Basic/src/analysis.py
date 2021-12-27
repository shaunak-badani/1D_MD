import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy import integrate
from src.system import System
from .units import Units
from .config import Config


class Analysis:
    def __init__(self):
        file_loc = "../../runs"
        if Config.ada:
            ada_path = os.path.join(Config.share_dir, Config.run_name)
            file_loc = "/scratch/shaunak/1D_Run/analysis"
            os.system("mkdir -p {}".format(file_loc))
            os.system("rsync -aPs ada:{} {}".format(ada_path, file_loc))
        
        self.file_path = os.path.join(file_loc, Config.run_name)
        self.images_path = os.path.join(os.getcwd(), "analysis_plots", Config.run_name)
        os.system("mkdir -p {}".format(self.images_path))

    def __get_scalars(self):
        file_path = self.file_path
        scalar_file = os.path.join(file_path, "scalars.txt")
        scalars = pd.read_csv(scalar_file, sep = ' ')
        return scalars

    def plot_energy(self):
        scalars = self.__get_scalars()

        pe = scalars["PE"].to_numpy()
        ke = scalars["KE"].to_numpy()
        pe_vals = pe
        ke_vals = ke

        tot_energy = scalars["TE"]
        steps = scalars["Time"]
        
        energies_path = os.path.join(self.images_path, "energies")
        os.system('mkdir -p {}'.format(energies_path))
        
        # Only KE
        fig = plt.figure(figsize = (21, 7))
        plt.plot(steps, ke_vals, linewidth = 1, color = 'red', alpha = 0.5)
        plt.scatter(steps, ke_vals, s = 2, c='red', alpha = 0.2)
        plt.yticks(fontsize = 22.5)
        plt.xticks(fontsize = 22.5)
        
        plt.xlabel("Steps", fontsize = 30)
        ylabel = plt.ylabel("Kinetic \n Energy", labelpad = 60, fontsize = 30)
        ylabel.set_rotation(0)
        ke_path = os.path.join(energies_path, "KE.png")
        plt.savefig(ke_path)
        plt.close()
        
        # Only PE
        fig = plt.figure(figsize = (21, 7))
        plt.plot(steps, pe_vals, linewidth = 1, color = 'blue', alpha = 0.5)
        plt.scatter(steps, pe_vals, s = 2, c='blue', alpha = 0.2)
        plt.yticks(fontsize = 22.5)
        plt.xticks(fontsize = 22.5)
        
        plt.xlabel("Steps", fontsize = 30)
        ylabel = plt.ylabel("Potential \n Energy", labelpad = 60, fontsize = 30)
        ylabel.set_rotation(0)
        pe_path = os.path.join(energies_path, "PE.png")
        plt.savefig(pe_path)
        plt.close()
        
        # Only TE
        fig = plt.figure(figsize = (21, 7))
        plt.plot(steps, tot_energy, linewidth = 1, color = 'green', alpha = 0.5)
        plt.scatter(steps, tot_energy, s = 2, c='green', alpha = 0.2)
        plt.yticks(fontsize = 22.5)
        plt.xticks(fontsize = 22.5)
        
        plt.xlabel("Steps", fontsize = 30)
        ylabel = plt.ylabel("Total \n Energy", labelpad = 60, fontsize = 30)
        ylabel.set_rotation(0)
        te_path = os.path.join(energies_path, "TE.png")
        plt.savefig(te_path)
        plt.close()
        
        # Collective plot
        fig = plt.figure(figsize = (21, 7))
        lw = 3
        plt.plot(steps, tot_energy, label="Total", linewidth = lw, color = 'green', alpha = 0.5)
        plt.plot(steps, ke_vals, label="Kinetic", linewidth = lw, color = 'red', alpha = 0.5)
        plt.plot(steps, pe_vals, label="Potential", linewidth = lw, color = 'blue', alpha = 0.5)
        
        plt.yticks(fontsize = 22.5)
        plt.xticks(fontsize = 22.5)
        
        plt.xlabel("Steps", fontsize = 30)
        ylabel = plt.ylabel("Total \n Energy", labelpad = 60, fontsize = 30)
        ylabel.set_rotation(0)
        
        plt.legend(fontsize = 25)
        e_path = os.path.join(self.images_path, "All_energies.png")
        plt.savefig(e_path)
        plt.close()

    def plot_temperature(self, temp, images_path):
        fig = plt.figure(figsize = (21, 7))
        scalars = self.__get_scalars()
        T = scalars["T"].to_numpy()

        
        steps = scalars["Time"].to_numpy()
        interval = 10
        plt.plot(steps[::interval], T[::interval], label = "Temperature", lw = 1, color = 'maroon', alpha = 0.5)
        plt.axhline(y = temp, linewidth = 3, color = 'red')

        plt.yticks(fontsize = 12)
        plt.xticks(fontsize = 12)
        
        plt.xlabel("No of Steps", fontsize = 15)
        ylabel = plt.ylabel("Temp \n erature", labelpad = 20, fontsize = 10)
        ylabel.set_rotation(0)
        t_path = os.path.join(images_path, "Temperature.png")
        plt.savefig(t_path)
        plt.close()
    
    def initialize_bins(self, bin_boundaries):
        self.bin_boundaries = bin_boundaries
    

    def plot_hprime(self, univ_path): 
        univ_energies = pd.read_csv(univ_path, sep = ' ')
        h_prime = univ_energies["Bath_System_Energy"].to_numpy()
        
        fig = plt.figure(figsize = (21, 7))
        steps = univ_energies["Step"].to_numpy()
        plt.axhline(y = h_prime.mean(), color = 'red')
        plt.plot(steps, h_prime, linewidth = 6, color = 'blue', alpha = 0.5, label = "H' ")
        
        
        plt.yticks(fontsize = 12)
        plt.xticks(fontsize = 12)
        
        plt.xlabel("Steps", fontsize = 15)
        plt.legend()
        ylabel = plt.ylabel("H`", labelpad = 100, fontsize = 15)
        ylabel.set_rotation(0)
        prime_path = os.path.join(self.images_path, "H_prime.png")
        plt.savefig(prime_path)
        plt.close()

    def velocity_distribution(self, vel, particle_index, images_path):

        vel_count, be = np.histogram(vel[:, particle_index], bins = 30, density = True)
        vel_coords = (be[1:] + be[:-1]) / 2

        m = 1
        expected_dist = np.exp(-vel_coords**2 / (2 * m * Units.kB * Config.T()))
        Z_vel = np.sqrt(2 * m * Units.kB * Config.T())
        expected_dist /= Z_vel
        plt.plot(vel_coords, expected_dist)
        plt.scatter(vel_coords, vel_count)
        
        # for i in vel_bins:
        #     plt.axvline(x = i, linewidth = 0.1)
        vel_dist = os.path.join(images_path, "vel_dist.png")
        plt.savefig(vel_dist)
         
        plt.close()

    
    
    def plot_probs(self, pos, particle_no, pot_energy, temperature, primary_replica):
        if not hasattr(self, 'bin_boundaries'):
            print("First Initialize bin boundaries!")
            return
        bin_boundaries = self.bin_boundaries
        boltzmann_integrand = np.empty(len(bin_boundaries) - 1)
        beta = 1 / (Units.kB * temperature)
        wells = np.arange(1, len(bin_boundaries))
        for i in wells:
            boltzmann_integrand[i - 1] = integrate.quad(lambda x: np.exp(-beta * pot_energy(x)), bin_boundaries[i-1], bin_boundaries[i])[0]

        well_counts = np.zeros_like(wells, dtype="float")
        for i in wells:
            lower_bound = bin_boundaries[i - 1]
            upper_bound = bin_boundaries[i]
            lies_in_well = np.logical_and(pos[:, particle_no] >= lower_bound, \
                                    pos[:, particle_no] < upper_bound)
            well_counts[i-1] = np.count_nonzero(lies_in_well)
        
        well_counts /= well_counts.sum()
        colors = ['r', 'g', 'b', 'm']
        markers=["+", "x", "o", "s"]
        boltzmann_integrand /= boltzmann_integrand.sum()


        for index, line in enumerate(boltzmann_integrand):
            plt.axhline(y = line, linewidth = 3, color = colors[index])
            plt.scatter(0, well_counts[index], marker = markers[index], color = colors[index], label='#{}'.format(index + 1) )
        plt.xlabel("Run number")
        plt.ylabel("Probability of particle in well")
        plt.legend()

        im_path = os.path.join(self.images_path, "boltzmann.png")
        plt.savefig(im_path)
        plt.close()

    def plot_free_energy(self, pos, particle_no, pot_energy):
        
        linspace = np.linspace(-2, 2.25, 1000)
        U = np.array([pot_energy(i) for i in linspace])
        plt.plot(linspace, U)
        plt.xlabel("Position")
        plt.ylabel("Energy")

        probs, bin_edges = np.histogram(pos[:, particle_no], bins = 40)
        probs = probs.astype('float')
        probs /= probs.sum()
        Config.replica_id = Config.primary_replica
        free_energy = -Units.kB * Config.T() * np.log(probs)
        free_energy -= free_energy.min()
        coords = (bin_edges[1:] + bin_edges[:-1]) / 2
        plt.plot(coords, free_energy, lw = 2, color='brown')

        im_path = os.path.join(self.images_path, "Free.png")
        plt.savefig(im_path)
        plt.close()

    def plot_maxwell(self, pos, particle_no, pot_energy, temperature, primary_replica):
            
        linspace = np.linspace(-2, 2.25, 1000)
        probs, bin_edges = np.histogram(pos[:, particle_no], bins = 500, density = True)
        coords = (bin_edges[1:] + bin_edges[:-1]) / 2

        U = np.array([pot_energy(i) for i in linspace])
        beta = 1 / (Config.T() * Units.kB)
        Z = integrate.quad(lambda x: np.exp(-beta * pot_energy(x)), -np.inf, np.inf)[0]

        Config.replica_id = Config.primary_replica
        expected_prob_dist = (1 / Z) * np.exp(-beta * U)
        plt.figure(figsize = (5, 4))
        plt.plot(linspace, expected_prob_dist, color = 'green', label = 'Expected Prob density')
        plt.xlabel(r'$x$', fontsize = 15)
        axy = plt.ylabel(r'$\rho (x)$', fontsize = 15)
        axy.set_rotation(0)

        plt.scatter(coords, probs, s = 10, color='purple', label = 'REMD Simulation Prob density')
        plt.legend()
        im_path = os.path.join(self.images_path, "Prob_dist.png")
        
        plt.savefig(im_path)
        plt.close()


    def pos_x_time(self, pos, steps, images_path):

        fig = plt.figure(figsize = (20, 3))

        plt.plot(steps, pos, lw = 0.5, color="black")
        plt.gca().spines["top"].set_visible(False)
        plt.gca().spines["right"].set_visible(False)
        plt.xticks([])
        plt.ylabel("Position")


        im_path = os.path.join(images_path, "pos_x_time.png")
        plt.savefig(im_path)
        plt.close()

class NVE_Analysis:

    def __init__(self):
        self.an = Analysis()

    def analyze(self):
        self.an.plot_energy()
        self.load_positions_and_velocities()
        self.an.pos_x_time(self.pos, self.steps, self.an.images_path)

    def load_positions_and_velocities(self):
        file_path = self.an.file_path
        positions = os.path.join(file_path, "p.txt")
        velocities = os.path.join(file_path, "v.txt")
        
        pos = np.loadtxt(positions)
        vel = np.loadtxt(positions)

        steps = pos[:, 0]
        pos = pos[:, 1:]
        vel = vel[:, 1:]

        self.vel = vel
        self.steps = steps
        self.pos = pos

    

class NVT_Analysis(NVE_Analysis):

    def __init__(self):
        self.an = Analysis()

    def analyze(self):
        self.an.plot_energy()
        self.load_positions_and_velocities()
        self.images_path = os.path.join(os.getcwd(), "analysis_plots", Config.run_name)
        self.an.pos_x_time(self.pos, self.steps, self.images_path)
        self.an.plot_temperature(Config.T(), self.images_path)
        self.load_univ()
        if hasattr(self, 'univ'):
            self.an.plot_hprime(self.univ_path)

        self.an.velocity_distribution(self.vel, 0, self.images_path)

    def load_univ(self):
        file_path = self.an.file_path
        univ_path = os.path.join(file_path, "univ_file.txt")
        if not os.path.isfile(univ_path):
            print("No surrounding energy has been noted during the simulation!\n")
            return
        self.univ_path = univ_path


class REMD_Analysis(NVE_Analysis):

    def __init__(self):
        self.an = Analysis()
        self.all_positions = []
        self.all_velocities = []
        
    def analyze(self):
        self.an.initialize_bins([-np.inf, -0.75, 0.25, 1.25, np.inf])
        root_dir = self.an.file_path

        for index, t in enumerate(Config.temperatures):
            self.an.file_path = os.path.join(self.an.file_path, str(index))
            self.load_positions_and_velocities()
            self.all_positions.append(self.pos)
            self.all_velocities.append(self.vel)
            images_path = self.an.images_path + "/" + str(index)
            if not os.path.isdir(images_path):
                os.mkdir(images_path)
            self.an.pos_x_time(self.pos, self.steps, images_path)
            self.an.plot_temperature(Config.temperatures[index], images_path)
            self.an.file_path = root_dir
        delattr(self, 'pos')
        delattr(self, 'vel')
        self.an.plot_maxwell(self.all_positions[Config.primary_replica], 0, System().pot_energy, Config.T(), Config.primary_replica)
        self.an.plot_probs(self.all_positions[Config.primary_replica], 0, System().pot_energy, Config.T(), Config.primary_replica)
        self.an.plot_free_energy(self.all_positions[Config.primary_replica], 0, System().pot_energy)

class RENS_Analysis(REMD_Analysis):

    def __init__(self):
        self.an = Analysis()
        self.all_positions = []
        self.all_velocities = []

    def free_energy(self, N, T):
        from scipy.integrate import quad
        beta = 1 / (Units.kB * T)
        pot_energy = System().pot_energy
        Z_single_particle = quad(lambda x : np.exp(-beta * pot_energy(x)), -np.inf, np.inf)[0]
        f = -N * np.log(Z_single_particle)
        f -= (N/2) * np.log(2 * np.pi / beta)
        return f

    def plot_multiple_probs(self):


        bins = [-np.inf, -0.75, 0.25, 1.25, np.inf]

        from scipy.integrate import quad
        beta = 1 / (Units.kB * Config.temperatures[Config.primary_replica])
        boltzmann_integrand = np.empty(len(bins) - 1)
        pot_energy = System().pot_energy
        for i in range(1, 5):
            boltzmann_integrand[i - 1] = quad(lambda x: np.exp(-beta * pot_energy(x)), bins[i-1], bins[i])[0]

        boltzmann_integrand /= boltzmann_integrand.sum()
        index = Config.primary_replica
        pos = self.all_positions[index]
        interval = 10000
        for particle_no in range(pos.shape[1]):
            images_path = os.path.join(self.an.images_path, "P_vs_t")
            if not os.path.isdir(images_path):
                os.mkdir(images_path)

            h = interval
            i = 0
            l = []
            t = []
            while h < pos.shape[0]:
                p, _ = np.histogram(pos[:h, particle_no], bins = bins)
                p = p.astype('float')
                p /= p.sum()
                l.append(p)
                i += 1
                h += interval
                
                t.append(self.steps[min(self.steps.shape[0] - 1, h)])
            l = np.array(l)
            colors = ['r', 'g', 'b', 'm']
            markers=["+", "x", "o", "s"]

            for i in range(4):
                plt.scatter(t, l[:, i], marker = markers[i], color=colors[i])
                plt.axhline(y = boltzmann_integrand[i], color = colors[i])

            plt.xlabel('Time (s)')
            _ = plt.ylabel('Prob.')
            _.set_rotation(0)
            plt.savefig(os.path.join(images_path, str(particle_no) + ".png"))
            plt.close()
            

    def plot_work_distribution(self, W_F, W_R, T_A, T_B):
        fig = plt.figure(figsize = (8, 6))
        p, be = np.histogram(W_F, bins = 50, density = True)
        coords = (be[1:] + be[:-1])/2
        plt.plot(coords, p, lw = 3, label = r'$\rho_F (w)$')

        p, be = np.histogram(W_R, bins = 50, density = True)
        coords = (be[1:] + be[:-1]) / 2
        plt.plot(-coords, p, lw = 3, label = r'$\rho_R (-w)$')


        f_A = self.free_energy(Config.num_particles, T_A)
        f_B = self.free_energy(Config.num_particles, T_B)

        free = f_B - f_A

        plt.axvline(x = free, color = 'red', lw = 3, label = r'$\Delta F$')
        plt.legend(loc = 'best', fontsize = 20)
        plt.xlabel(r'$w$', fontsize = 15)
        y = plt.ylabel(r'$\rho (w)$', fontsize = 20)
        y.set_rotation(0)

        im_path = os.path.join(self.an.images_path, "work.png")
        plt.savefig(im_path)
        plt.close()

    def get_simulation_data(self):

        # W_mean, p_acc
        W_A = self.exchanges['W_A'].to_numpy()
        W_B = self.exchanges['W_B'].to_numpy()
        w = W_A + W_B
        w_mean = w.mean()
        p_acc = self.exchanges['Exchanged'].mean()

        # X, f_sw
        tau = Config.tau
        dt = 1e-3
        k = self.exchanges['Time'].to_numpy()
        final_time = Config.num_steps * dt
        ending_points = k - tau
        ending_points = np.insert(ending_points, ending_points.size, final_time)
        k = np.insert(k, 0, 0)
        tau_eq = ending_points - k
        tau_eq = tau_eq.mean()

        X = tau / tau_eq
        f_sw = X / (1 + X)

        # t_c, t_star
        def auto_corr(x, tau):
            len_data = len(x[tau:])
            mean = x.mean()
            num = (x[:len_data] * x[tau:tau + len_data]).mean() - mean**2
            var = (x**2).mean() - (mean)**2
            return num / var

        n_4t = np.sum(self.all_positions[Config.primary_replica] >= 1.25, axis = 1)
        c_t = np.array([auto_corr(n_4t, i) for i in range(n_4t.size)])
        t_c = c_t.sum()
        t_star = (1 + X) * t_c

        data_object = {'W_mean' : w_mean, 'p_acc' : p_acc, 'X' : X, 'f_sw' : f_sw, 't_star' : t_star}
        dict_df = pd.DataFrame({ key:pd.Series(value) for key, value in data_object.items() })
        dict_df
        dict_df.to_csv(os.path.join(self.an.images_path, "run_summary.dat"), index = False)
        
    def analyze(self):
        self.an.initialize_bins([-np.inf, -0.75, 0.25, 1.25, np.inf])
        root_dir = self.an.file_path

        for index, t in enumerate(Config.temperatures):
            self.an.file_path = os.path.join(self.an.file_path, str(index))
            self.load_positions_and_velocities()
            ind = (self.pos[:, -1] == 0)
            pos = self.pos[ind, :-1]
            vel = self.vel[ind, :-1]
            steps = self.steps[ind]
            self.all_positions.append(pos)
            self.all_velocities.append(vel)
            images_path = self.an.images_path + "/" + str(index)
            if not os.path.isdir(images_path):
                os.mkdir(images_path)
            self.an.pos_x_time(pos, steps, images_path)
            self.an.plot_temperature(Config.temperatures[index], images_path)
            self.an.file_path = root_dir
        delattr(self, 'pos')
        delattr(self, 'vel')
        self.an.plot_maxwell(self.all_positions[Config.primary_replica], 0, System().pot_energy, Config.T(), Config.primary_replica)
        self.an.plot_probs(self.all_positions[Config.primary_replica], 0, System().pot_energy, Config.T(), Config.primary_replica)
        # self.an.plot_free_energy(self.all_positions[Config.primary_replica], 0, System().pot_energy)

        self.exchanges = pd.read_csv(os.path.join(self.an.file_path, "exchanges.txt"), sep = ',')
        T_A = Config.temperatures[self.exchanges['Src'][0]]
        T_B = Config.temperatures[self.exchanges['Dest'][0]]
        self.plot_work_distribution(self.exchanges['W_A'].to_numpy(), self.exchanges['W_B'].to_numpy(), T_A, T_B)
        self.plot_multiple_probs()
        # self.get_simulation_data()
        

