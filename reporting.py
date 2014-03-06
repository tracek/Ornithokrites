# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 18:05:56 2014

@author: Lukasz Tracewski

Reporting module
"""

import os, sys
import logging
import smtplib
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class Reporter(object):
    
    def __init__(self, app_config):
        """
        Reporting results to the user
        
        Parameters
        ----------
        app_config : AppConfig
            AppConfig namedtuple defined in configuration.py.
        """
        self.start_time = time.time() # Log start up time
        
        # Clean up
        root = logging.getLogger()
        if root.handlers:
            for handler in root.handlers:
                root.removeHandler(handler)  
        self.cleanup()
        # and create our logs
        self.Log = self._create_logger('log.html', app_config.data_store, app_config.write_stdout)
        self.DevLog = self._create_logger('devlog.html', app_config.data_store)
        self._config = app_config

    def write_results(self, kiwi_result, individual_calls, filename, audio, rate, segmented_sounds):
        """
        Write results to log files.
        
        Parameters
        -----------
        kiwi_result : string
            Result of identification: Male, Female, Male and Female or None.
        individual_calls : 1-d array of int
            Result of identification of individual calls (0-None, 1-Female, 2-Male, 3-Male and Female).
        filename : string
            Path to the audio file.
        audio : 1-d array
            Monaural audio sample.
        rate : int
            Sample rate in Hz.
        segmented_sounds : list of (int, int)
            List of tuples defining start and end of each call
        
        Returns
        -----------
        Nothing
        """
        self.Log.info('%s: %s' % (filename, kiwi_result))
        
        self.DevLog.info('<h2>%s</h2>' % kiwi_result)
        self.DevLog.info('<h2>%s</h2>' % filename.replace('/var/www/results/',''))
        
        if self._config.delete_data:
            os.remove(filename)
        else:
            self.DevLog.info('<audio controls><source src="%s" type="audio/wav"></audio>', 
                         filename.replace('/var/www/',''))            
            
        
        # Plot spectrogram
        plt.ioff()
        plt.specgram(audio, NFFT=2**11, Fs=rate)
        # and mark on it with vertical lines found audio features
        for i, (start, end) in enumerate(segmented_sounds):
            start /= rate
            end /= rate
            plt.plot([start, start], [0, 4000], lw=1, c='k', alpha=0.2, ls='dashed')
            plt.plot([end, end], [0, 4000], lw=1, c='g', alpha=0.4)
            plt.text(start, 4000, i, fontsize=8)
            if individual_calls[i] == 1:
                plt.plot((start + end) / 2, 3500, 'go')
            elif individual_calls[i] == 2:
                plt.plot((start + end) / 2, 3500, 'bv')
        plt.axis('tight')
        title = plt.title(kiwi_result)
        title.set_y(1.03)
        spectrogram_sample_name = filename + '.png'
        plt.savefig(spectrogram_sample_name)
        plt.clf()
        path = spectrogram_sample_name.replace('/var/www/','')
        self.DevLog.info('<img src="%s" alt="Spectrogram">', path)
        self.DevLog.info('<hr>')
        
    def write_results_parallel(self, outq):
        """
        Write results from a queue to log files.
        
        Parameters
        -----------
        outq : multiprocessing.Queue
            Queue from which results will be read. Content of the queue is the same as
            explained for write_results method.
        
        Returns
        ----------
        Nothing
        """
        
        for works in range(self._config.no_processes):
            for kiwi_result, individual_calls, filename, audio, rate, segmented_sounds, ex in iter(outq.get, "STOP"):
                self.Log.info('%s: %s' % (filename.replace('/var/www/results/',''), kiwi_result))
                
                if ex:
                    self.Log.exception('Problem encountered during noise reduction: %s', ex.message)
                    self.DevLog.exception(ex)
                
                self.DevLog.info('<h2>%s</h2>' % kiwi_result)
                self.DevLog.info('<h2>%s</h2>' % filename.replace('/var/www/results/',''))
                
                if self._config.delete_data:
                    os.remove(filename)
                else:
                    self.DevLog.info('<audio controls><source src="%s" type="audio/wav"></audio>', 
                                 filename.replace('/var/www/',''))                    
                    
                if self._config.with_spectrogram:
                    # Plot spectrogram
                    plt.ioff()
                    plt.specgram(audio, NFFT=2**11, Fs=rate)
                    # and mark on it with vertical lines found audio features
                    for i, (start, end) in enumerate(segmented_sounds):
                        start /= rate
                        end /= rate
                        plt.plot([start, start], [0, 4000], lw=1, c='k', alpha=0.2, ls='dashed')
                        plt.plot([end, end], [0, 4000], lw=1, c='g', alpha=0.4)
                        plt.text(start, 4000, i, fontsize=8)
                        if individual_calls[i] == 1:
                            plt.plot((start + end) / 2, 3500, 'go')
                        elif individual_calls[i] == 2:
                            plt.plot((start + end) / 2, 3500, 'bv')
                    plt.axis('tight')
                    title = plt.title(kiwi_result)
                    title.set_y(1.03)
                    spectrogram_sample_name = filename + '.png'
                    plt.savefig(spectrogram_sample_name)
                    plt.clf()
                    path = spectrogram_sample_name.replace('/var/www/','')
                    self.DevLog.info('<img src="%s" alt="Spectrogram">', path)
                    
                self.DevLog.info('<hr>')
        
        if self._config.mail:
            self.send_email()
        self.cleanup()
        
    def cleanup(self):
        """ Print execution time, remove all handlers from logs and stop logging. """
        log = logging.getLogger('log.html')
        devlog = logging.getLogger('devlog.html')
        elapsed_time = time.strftime('%H:%M:%S', time.gmtime(time.time() - self.start_time))
        log.info('Execution time: %s', elapsed_time)    
        log.handlers = []
        devlog.handlers = []
        logging.shutdown()
    
    def send_email(self):
        """ 
        Send e-mail to a user once execution is completed. Meant for the web interface. To work
        requires credentials for a given e-mail account
        """
            
        email_credentials_location = os.path.join(self._config.program_directory, "reporting.config")
        if not os.path.isfile(email_credentials_location):
            self.Log.error('Missing file %s with credentials. Sending e-mail has failed')
            sys.exit(1)
        with open (email_credentials_location, "r") as credentials:
            (gmail_user, gmail_pwd) = credentials.read().splitlines()
        FROM = 'Kiwi-Finder no-reply'
        TO = [self._config.mail, 'lukasz.tracewski@gmail.com'] #must be a list
        SUBJECT = "Kiwi-Finder: your data is ready"
        TEXT = """
               Kiwi-Finder.info has finished processing your recordings.
               Report is available here: http://kiwi-finder.info/results/log.html
               
               Cheers,
               http://kiwi-finder.info
               """
    
        # Prepare actual message
        message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        try:
            #server = smtplib.SMTP(SERVER) 
            server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_pwd)
            server.sendmail(FROM, TO, message)
            #server.quit()
            server.close()
            self.Log.info('Sending e-mail to %s successful', self._config.mail)
        except Exception, e:
            self.log_exception(e)
            
    def log_exception(self, exception, message=''):
        self.Log.info(message)
        self.Log.exception(exception)
        

    def _create_logger(self, name, path, stdout=False):
        if not os.path.exists(path):
            os.makedirs(path)
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(os.path.join(path, name),'w')
        formatter = logging.Formatter('%(message)s <br/>')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.info('<!DOCTYPE html>')
        if stdout:
            logger.addHandler(logging.StreamHandler()) # for standard output (console)
        return logger        
        
    