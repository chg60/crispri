import tkinter as tk
import tkinter.messagebox
import requests
import os
import json
from ui.windows.MainWindow import MainWindow


class MainWindowController:
    def __init__(self):
        self.window = MainWindow(controller=self)
        self.window.launch()

    def get_primers(self, name, sequence, mode, crispr, save_file=None):
        print(name, mode, crispr, save_file)
        # unchanging variables
        valid_dnas = ["A", "C", "G", "T"]
        strong_pams = ['CTTCT','ATTCT','TTTCT','CTTCC','GTTCT','TTTCC','ATGCT',
        'CTCCT','ATCCT','TTGCT','GTTCC','ATTCC','CTGCT','TTCCT','GTCCT']
        weak_pams = ['CTCCC','ATCCC','TTCCC','GTGCT','GTCCC','ATGCC','CTGCC',
        'TTGCC','GTGCC']

        # variables that could be filled in
        invalid_dnas = []
        coding_pams = {}
        coding_reverse_primers = {}
        coding_forward_primers = {}

        # save function inputs and coerce input sequence to all capitalized letters
        name = name
        save_file = save_file
        coding_sequence = sequence.upper()

        # check for non-dna letters
        for letter in sequence:
            if letter not in valid_dnas:
                invalid_dnas.append(letter)

        # if any non-dna letters were found, warn the user, and return
        invalid_dnas = set(invalid_dnas)
        if len(invalid_dnas) > 0:
            if len(invalid_dnas) == 1:
                tkinter.messagebox.showinfo(title="Invalid Nucleotide",
                message="{} was found in your sequence. Please make sure your sequence only contains A, C, G, or T nucleotides, and try again.".format(list(invalid_dnas)[0]))
                return
            else:
                tkinter.messagebox.showinfo(title="Invalid Nucleotides",
                message="{} were found in your sequence. Please make sure your sequence only contains A, C, G, or T nucleotides, and try again.".format(list(invalid_dnas)[0] + ", ".join(list(invalid_dnas)[1:])))
                return

        # if crispr mode is 1, we'll need a couple of additional variables to store any PAMs/primers for the template strand as well
        if crispr == 1:
            template_pams = {}
            template_reverse_primers = {}
            template_forward_primers = {}
            template_sequence = reverse_complement(coding_sequence)

        if crispr == 0:
            # if no non-dna letters were found, proceed in either of the two modes: weak or strong
            if mode == "strong":
                # iterate through the pams
                for pam in strong_pams:
                    # if a particular pam is found in the sequence
                    if pam in coding_sequence:
                        # log where the pam is found
                        coding_pams[pam] = coding_sequence.index(pam)
                        # if there's enough sequence left to generate primers, do so
                        if len(coding_sequence[coding_sequence.index(pam):]) > 27:
                            rev_primer_start = coding_sequence.index(pam) + 7
                            rev_primer_end = coding_sequence.index(pam) + 27
                            raw_rev_primer = coding_sequence[rev_primer_start:rev_primer_end]
                            reverse_primer = "AAAC" + raw_rev_primer + "C"
                            raw_fwd_primer = reverse_complement(raw_rev_primer)
                            forward_primer = "GGGAG" + raw_fwd_primer
                            coding_forward_primers[pam] = forward_primer
                            coding_reverse_primers[pam] = reverse_primer

                # if no pam sites were found, notify the user
                if len(coding_pams) == 0:
                    result = tkinter.messagebox.askyesnocancel(title="No Strong PAM Sites Found",
                    message="No strong PAM sites were found in the coding sequence. Would you like to try searching for weaker PAM sites?",
                    default=tk.messagebox.CANCEL)
                    if result is None or result == False:
                        return
                    else:
                        self.get_primers(name=name, sequence=coding_sequence, save_file=save_file, mode="weak", crispr=crispr)
                else:
                    primer_text = ""
                    if save_file:
                        output_file = open(save_file, "w")
                        output_file.write(">{}\n{}\n\n".format(name, coding_sequence))

                        for pam in coding_pams.keys():
                            output_file.write("{}\n".format(reverse_complement(pam)))
                            primer_text = primer_text + "{}\n".format(reverse_complement(pam))
                            output_file.write("\tForward Primer\t5'-{}-3'\n".format(coding_forward_primers[pam]))
                            primer_text = primer_text + "\tForward Primer\n5'-{}-3'\n".format(coding_forward_primers[pam])
                            output_file.write("\tReverse Primer\t5'-{}-3'\n".format(coding_reverse_primers[pam]))
                            primer_text = primer_text + "\tReverse Primer\n5'-{}-3'\n".format(coding_reverse_primers[pam])

                        output_file.close()

                        tkinter.messagebox.showinfo(title="Done!",
                        message="The following PAM sites were found. If you chose a save file, primers are saved there. \n{}".format(primer_text))
                    else:
                        for pam in coding_pams.keys():
                            primer_text = primer_text + "{}\n".format(reverse_complement(pam))
                            primer_text = primer_text + "\tForward Primer\n5'-{}-3'\n".format(coding_forward_primers[pam])
                            primer_text = primer_text + "\tReverse Primer\n5'-{}-3'\n".format(coding_reverse_primers[pam])

                        tkinter.messagebox.showinfo(title="Done!",
                        message="The following PAM sites were found. If you chose a save file, primers are saved there. \n{}".format(primer_text))
            elif mode == "weak":
                # iterate through the pams
                for pam in weak_pams:
                    # if a particular pam is found in the sequence
                    if pam in sequence:
                        # log where the pam is found
                        coding_pams[pam] = coding_sequence.index(pam)
                        # if there's enough sequence left to generate primers, do so
                        if len(coding_sequence[coding_sequence.index(pam):]) > 27:
                            rev_primer_start = coding_sequence.index(pam) + 7
                            rev_primer_end = coding_sequence.index(pam) + 27
                            raw_rev_primer = coding_sequence[rev_primer_start:rev_primer_end]
                            reverse_primer = "AAAC" + raw_rev_primer + "C"
                            raw_fwd_primer = reverse_complement(raw_rev_primer)
                            forward_primer = "GGGAG" + raw_fwd_primer
                            coding_forward_primers[pam] = forward_primer
                            coding_reverse_primers[pam] = reverse_primer

                # if no pam sites were found, notify the user
                if len(coding_pams) == 0:
                    tkinter.messagebox.showinfo(title="No PAM Sites Found",
                    message="No PAM sites were found in your input sequence. Please try a new sequence, or exit the program.")
                    return
                else:
                    primer_text = ""
                    if save_file:
                        output_file = open(save_file, "w")
                        output_file.write(">{}\n{}\n\n".format(name, coding_sequence))

                        primer_text = primer_text + "\nCoding strand:\n\n"
                        for pam in coding_pams.keys():
                            output_file.write("{}\n".format(reverse_complement(pam)))
                            primer_text = primer_text + "{}\n".format(reverse_complement(pam))
                            output_file.write("\tForward Primer\t5'-{}-3'\n".format(forward_primer[pam]))
                            primer_text = primer_text + "\tForward Primer\n5'-{}-3'\n".format(coding_forward_primers[pam])
                            output_file.write("\tReverse Primer\t5'-{}-3'\n\n".format(reverse_primer[pam]))
                            primer_text = primer_text + "\tReverse Primer\n5'-{}-3'\n".format(coding_reverse_primers[pam])

                        output_file.close()

                        tkinter.messagebox.showinfo(title="Done!",
                        message="The following PAM sites were found. If you chose a save file, primers are saved there. \n{}".format(primer_text))
                    else:
                        for pam in coding_pams.keys():
                            primer_text = primer_text + "{}\n".format(reverse_complement(pam))
                            primer_text = primer_text + "\tForward Primer\n5'-{}-3'\n".format(coding_forward_primers[pam])
                            primer_text = primer_text + "\tReverse Primer\n5'-{}-3'\n".format(coding_reverse_primers[pam])

                        tkinter.messagebox.showinfo(title="Done!",
                        message="The following PAM sites were found. If you chose a save file, primers are saved there. \n{}".format(primer_text))
            return

        elif crispr == 1:
            # if no non-dna letters were found, proceed in either of the two modes: weak or strong
            if mode == "strong":
                # iterate through the pams
                for pam in strong_pams:
                    # if a particular pam is found in the sequence
                    if pam in coding_sequence:
                        # log where the pam is found
                        coding_pams[pam] = coding_sequence.index(pam)
                        # if there's enough sequence left to generate primers, do so
                        if len(coding_sequence[coding_sequence.index(pam):]) > 27:
                            rev_primer_start = coding_sequence.index(pam) + 7
                            rev_primer_end = coding_sequence.index(pam) + 27
                            raw_rev_primer = coding_sequence[rev_primer_start:rev_primer_end]
                            reverse_primer = "AAAC" + raw_rev_primer + "C"
                            raw_fwd_primer = reverse_complement(raw_rev_primer)
                            forward_primer = "GGGAG" + raw_fwd_primer
                            coding_forward_primers[pam] = forward_primer
                            coding_reverse_primers[pam] = reverse_primer
                    # if that pam is found in the template sequence
                    if pam in template_sequence:
                        # log where it is found
                        template_pams[pam] = template_sequence.index(pam)
                        if len(template_sequence[template_sequence.index(pam):]) > 27:
                            rev_primer_start = template_sequence.index(pam) + 7
                            rev_primer_end = template_sequence.index(pam) + 27
                            raw_rev_primer = template_sequence[rev_primer_start:rev_primer_end]
                            reverse_primer = "AAAC" + raw_rev_primer + "C"
                            raw_fwd_primer = reverse_complement(raw_rev_primer)
                            forward_primer = "GGGAG" + raw_fwd_primer
                            template_forward_primers[pam] = forward_primer
                            template_reverse_primers[pam] = reverse_primer

                # if no pam sites were found, notify the user
                if len(coding_pams) == 0 and len(template_pams) == 0:
                    result = tkinter.messagebox.askyesnocancel(title="No Strong PAM Sites Found",
                    message="No strong PAM sites were found in the coding sequence or the template sequence. Would you like to try searching for weaker PAM sites?",
                    default=tk.messagebox.CANCEL)
                    if result is None or result == False:
                        return
                    else:
                        self.get_primers(name=name, sequence=coding_sequence, save_file=save_file, mode="weak", crispr=crispr)
                else:
                    primer_text = ""
                    if save_file:
                        output_file = open(save_file, "w")
                        output_file.write(">{}\n{}\n\n".format(name, coding_sequence))

                        primer_text = primer_text + "\nCoding strand:\n\n"
                        for pam in coding_pams.keys():
                            output_file.write("{}\n".format(reverse_complement(pam)))
                            primer_text = primer_text + "{}\n".format(reverse_complement(pam))
                            output_file.write("\tForward Primer\t5'-{}-3'\n".format(coding_forward_primers[pam]))
                            primer_text = primer_text + "\tForward Primer\n5'-{}-3'\n".format(coding_forward_primers[pam])
                            output_file.write("\tReverse Primer\t5'-{}-3'\n\n".format(coding_reverse_primers[pam]))
                            primer_text = primer_text + "\tReverse Primer\n5'-{}-3'\n".format(coding_reverse_primers[pam])

                        output_file.write(">{}\n{}\n\n".format(name, template_sequence))

                        primer_text = primer_text + "\nTemplate strand:\n\n"
                        for pam in template_pams.keys():
                            output_file.write("{}\n".format(reverse_complement(pam)))
                            primer_text = primer_text + "{}\n".format(reverse_complement(pam))
                            output_file.write("\tForward Primer\t5'-{}-3'\n".format(template_forward_primers[pam]))
                            primer_text = primer_text + "\tForward Primer\n5'-{}-3'\n".format(template_forward_primers[pam])
                            output_file.write("\tReverse Primer\t5'-{}-3'\n".format(template_reverse_primers[pam]))
                            primer_text = primer_text + "\tReverse Primer\n5'-{}-3'\n".format(template_reverse_primers[pam])

                        output_file.close()
                        tkinter.messagebox.showinfo(title="Done!",
                        message="The following PAM sites were found. If you chose a save file, primers are saved there. \n{}".format(primer_text))
                    else:
                        primer_text = primer_text + "\nCoding strand:\n\n"
                        for pam in coding_pams.keys():
                            primer_text = primer_text + "{}\n".format(reverse_complement(pam))
                            primer_text = primer_text + "\tForward Primer\n5'-{}-3'\n".format(coding_forward_primers[pam])
                            primer_text = primer_text + "\tReverse Primer\n5'-{}-3'\n".format(coding_reverse_primers[pam])

                        primer_text = primer_text + "\nTemplate strand:\n\n"
                        for pam in template_pams.keys():
                            primer_text = primer_text + "{}\n".format(reverse_complement(pam))
                            primer_text = primer_text + "\tForward Primer\n5'-{}-3'\n".format(template_forward_primers[pam])
                            primer_text = primer_text + "\tReverse Primer\n5'-{}-3'\n".format(template_reverse_primers[pam])

                        tkinter.messagebox.showinfo(title="Done!",
                        message="The following PAM sites were found. If you chose a save file, primers are saved there. \n{}".format(primer_text))

            elif mode == "weak":
                # iterate through the pams
                for pam in weak_pams:
                    # if a particular pam is found in the sequence
                    if pam in sequence:
                        # log where the pam is found
                        coding_pams[pam] = coding_sequence.index(pam)
                        # if there's enough sequence left to generate primers, do so
                        if len(coding_sequence[coding_sequence.index(pam):]) > 27:
                            rev_primer_start = coding_sequence.index(pam) + 7
                            rev_primer_end = coding_sequence.index(pam) + 27
                            raw_rev_primer = coding_sequence[rev_primer_start:rev_primer_end]
                            reverse_primer = "AAAC" + raw_rev_primer + "C"
                            raw_fwd_primer = reverse_complement(raw_rev_primer)
                            forward_primer = "GGGAG" + raw_fwd_primer
                            coding_forward_primers[pam] = forward_primer
                            coding_reverse_primers[pam] = reverse_primer
                    # if that pam is found in the template sequence
                    if pam in template_sequence:
                        # log where it is found
                        template_pams[pam] = template_sequence.index(pam)
                        if len(template_sequence[template_sequence.index(pam):]) > 27:
                            rev_primer_start = template_sequence.index(pam) + 7
                            rev_primer_end = template_sequence.index(pam) + 27
                            raw_rev_primer = template_sequence[rev_primer_start:rev_primer_end]
                            reverse_primer = "AAAC" + raw_rev_primer + "C"
                            raw_fwd_primer = reverse_complement(raw_rev_primer)
                            forward_primer = "GGGAG" + raw_fwd_primer
                            template_forward_primers[pam] = forward_primer
                            template_reverse_primers[pam] = reverse_primer

                # if no pam sites were found, notify the user
                if len(coding_pams) == 0 and len(template_pams) == 0:
                    tkinter.messagebox.showinfo(title="No PAM Sites Found",
                    message="No PAM sites were found in your input sequence. Please try a new sequence, or exit the program.")
                    return
                else:
                    primer_text = ""
                    if save_file:
                        output_file = open(save_file, "w")
                        output_file.write(">{}\n{}\n\n".format(name, coding_sequence))

                        primer_text = primer_text + "\nCoding strand:\n\n"
                        for pam in coding_pams.keys():
                            output_file.write("{}\n".format(reverse_complement(pam)))
                            primer_text = primer_text + "{}\n".format(reverse_complement(pam))
                            output_file.write("\tForward Primer\t5'-{}-3'\n".format(coding_forward_primers[pam]))
                            primer_text = primer_text + "\tForward Primer\n5'-{}-3'\n".format(coding_forward_primers[pam])
                            output_file.write("\tReverse Primer\t5'-{}-3'\n\n".format(coding_reverse_primers[pam]))
                            primer_text = primer_text + "\tReverse Primer\n5'-{}-3'\n".format(coding_reverse_primers[pam])

                        output_file.write(">{}\n{}\n\n".format(name, template_sequence))

                        primer_text = primer_text + "\nTemplate strand:\n\n"
                        for pam in template_pams.keys():
                            output_file.write("{}\n".format(reverse_complement(pam)))
                            primer_text = primer_text + "{}\n".format(reverse_complement(pam))
                            output_file.write("\tForward Primer\t5'-{}-3'\n".format(template_forward_primers[pam]))
                            primer_text = primer_text + "\tForward Primer\n5'-{}-3'\n".format(template_forward_primers[pam])
                            output_file.write("\tReverse Primer\t5'-{}-3'\n".format(template_reverse_primers[pam]))
                            primer_text = primer_text + "\tReverse Primer\n5'-{}-3'\n".format(template_reverse_primers[pam])

                        output_file.close()
                        tkinter.messagebox.showinfo(title="Done!",
                        message="The following PAM sites were found. If you chose a save file, primers are saved there. \n{}".format(primer_text))
                    else:
                        primer_text = primer_text + "\nCoding strand:\n\n"
                        for pam in coding_pams.keys():
                            primer_text = primer_text + "{}\n".format(reverse_complement(pam))
                            primer_text = primer_text + "\tForward Primer\n5'-{}-3'\n".format(coding_forward_primers[pam])
                            primer_text = primer_text + "\tReverse Primer\n5'-{}-3'\n".format(coding_reverse_primers[pam])

                        primer_text = primer_text + "\nTemplate strand:\n\n"
                        for pam in template_pams.keys():
                            primer_text = primer_text + "{}\n".format(reverse_complement(pam))
                            primer_text = primer_text + "\tForward Primer\n5'-{}-3'\n".format(template_forward_primers[pam])
                            primer_text = primer_text + "\tReverse Primer\n5'-{}-3'\n".format(template_reverse_primers[pam])

                        tkinter.messagebox.showinfo(title="Done!",
                        message="The following PAM sites were found. If you chose a save file, primers are saved there. \n{}".format(primer_text))
            return

    def open_documentation(self):
        os.system("open -a Preview userguide.pdf")

    def report_bug(self):
        with open("contact.json", "r") as filehandle:
            contact = json.load(filehandle)
        message="Please email {} at {} with any bugs. Please write '{}' in the subject line. In the body of your email, please include a {}, the {}, the {}, {}, {} and {} number {}.".format(contact['name'], contact['email'], contact['subject'], contact['include'][0], contact['include'][1], contact['include'][2], contact['include'][3], contact['include'][4], contact['include'][5], contact['version'])
        tkinter.messagebox.askokcancel(title="Bug Reporting", message=message)

    def check_for_updates(self):
        # local version
        f = open("version.txt", "r")
        local_version = f.readline()
        f.close()

        # remote version
        response = requests.get("https://raw.github.com/chg60/crispri/master/data/version.txt")
        remote_version = response.text.rstrip("\n")
        if remote_version > local_version:
            update = tkinter.messagebox.askyesnocancel(title="Updates Available",
            message="Updates are available. Would you like to download them now? This should take a few seconds, and the new application will be found in your Downloads folder.")
        else:
            tkinter.messagebox.showinfo(title="No Updates Available",
            message="There are no updates available at this time.")
            update = False
        if update == True:
            os.system("cd ~/Downloads/; curl -LO https://raw.github.com/chg60/crispri/master/MacOSX-version{}.zip; unzip MacOSX-version{}.zip; rm MacOSX-version{}.zip".format(remote_version, remote_version, remote_version))
            # os.system("unzip MacOSX-version{}.zip".format(remote_version))
            # os.system("rm MacOSX-version{}.zip".format(remote_version))
            tkinter.messagebox.showinfo(title="Program Restart Required",
            message="The updated application can be found in your Downloads.  You'll need to manually drag it into your Applications folder to overwrite this version.")

    def quit(self):
        title = "Quitting Program..."
        message = "Are you sure you want to quit Mycobacterial CRISPRi Primer Designer?"

        result = tkinter.messagebox.askyesnocancel(title=title, message=message, default=tkinter.messagebox.CANCEL)

        if result is None or result == False:
            return

        self.window.destroy()

def reverse_complement(sequence):
    complement_lookup = {"A":"T", "C":"G", "G":"C", "T":"A"}
    complementary_sequence = ""
    for letter in sequence[-1::-1]:
        complementary_sequence = complementary_sequence + complement_lookup[letter]
    return complementary_sequence
