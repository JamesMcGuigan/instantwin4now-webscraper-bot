#!/usr/bin/python
import sys

import os
import random
import re
from scrape_utils import *
import shlex
import string
import subprocess
import urllib
import urllib2




#db = sqlite3.connect("comp.db")
#db.isolation_level = None
#db = db.cursor()


opener      = urllib2.build_opener()
domain = ""
list_prefix = ""
mystery_prefix = ""
logins = []
cats   = []
comps_entered = {};






def get_comps_left_count(id):
    if domain == "http://www.win4now.co.uk": 
        url = domain + "/prize-draws-not-entered?ID=" + id
        html = get_url(url);
        urls = unique( re.findall('<a"[^>]*href="(/competition/[^<>"]*?)"[^>]*class="comp[^>]*>', html, re.S) )
        return len(urls);

    else:
        url = domain + "/index?ID="+id;
        html = get_url(url);
        match = re.findall('Weekly entries remaining:\s*(\d+)', html, re.S | re.I);
        count = int(match[0]) if len(match) else -1;
        return count;

def get_list_urls( id, param ):
    url = domain + list_prefix + "?ID="+id+param;
    html = get_url(url);
    urls = re.findall('<a[^>]*href="([^>"]*)"[^>]*class="comps-page-link"[^>]*>', html, re.S | re.I);
    urls = unique( urls )
    print "||||| PAGE COUNT URL: ", url, "|"*10; print urls;
    return urls;

def get_comp_urls( url, id ):
    html = get_url(url);
    urls = unique( re.findall('<a[^>]*href="(/competition/[^<>"]*?)"[^>]*class="comp[^>]*>', html, re.S) )
    urls = [ re.sub("ID=\w+","ID="+id, url, re.I) for url in urls ];
    print "||||| LIST PAGE URL: ", url, "|"*10; print urls;
    return urls;


def extract_win_message( html, comp_url ):
    message = re.findall( 'Error: [^<]*', html, re.S | re.I );
    if len(message) > 0: print "MESSAGE: ", message[0]; return;

    message = re.findall( "You didn't guess the right combination this time", html, re.S | re.I );
    if len(message) > 0: print "MESSAGE: ", message[0]; return;

    print "\n\n" + "*"*40 + "\n" + "*"*40 + "\n\n"
    print "WIN " * 10
    print "\n\n" + "*"*40 + "\n" + "*"*40 + "\n\n"
    print domain+"/"+comp_url
    print "\n\n" + "*"*40 + "\n" + "*"*40 + "\n\n"
    print html
    print "\n\n" + "*"*40 + "\n" + "*"*40 + "\n\n"
    print domain+"/"+comp_url
    print "\n\n" + "*"*40 + "\n" + "*"*40 + "\n\n"
    print "WIN " * 10
    print "\n\n" + "*"*40 + "\n" + "*"*40 + "\n\n"

    email_self("You are a winner! "+domain+"/"+comp_url, html)


def open_mystery_box( html, id ):
    href = re.findall( mystery_prefix + '\?open=envelope&ID=[^>"]*', html, re.S | re.I );

    #mystery_box_page = get_url( domain+"/mystery-box\?open=envelope&ID="+id );
    if len(href):
        mystery_box_page = get_url( domain+href[0] );
        links = re.findall( mystery_prefix + '\?multiple[^>"]*', mystery_box_page, re.S | re.I );
        if len(links):
            link = random.choice(links);
            get_url( domain+link );
            print "ENTERED Mystery Box: ", link
        else:
            print "FAILED Mystery Box: ", link



def spider():
    for id in logins:
        cat = random.choice(cats);

        count = 1;
        loop = 0;
        while count > 0: # stop infinate loop
            loop = loop + 1;
            if domain == "http://www.win4now.co.uk" and loop > 5: break;

            count = get_comps_left_count(id);
            print domain + " ID: %s - CAT: %s  - REMAINING: %s" % (id, cat, count);
                
            #for list_url in get_list_urls( id, "&cat="+cat):
            #if count == 0: print "END: 50 Entries POSTED"; break;

            list_url = list_prefix + "?ID=%s" % id;
            if cat != "": list_url = list_url + "&cat=%s" % cat;

            print "***** LIST URL: ", domain+list_url, "*"*10;

            comp_urls = get_comp_urls( domain+list_url, id );
            if len(comp_urls) == 0: cat = ""; # reset cat if we run out

            for comp_url in comp_urls:
                comp_name = re.sub("&ID.*", "", comp_url);
                if comp_name in comps_entered: continue;
                else: comps_entered[comp_name] = 1;

                print
                print
                print
                print "----- COMP URL: ", domain+comp_url, "-"*10;
                lucky_page = get_url( domain+comp_url );

                if domain != "http://www.win4now.co.uk":
                    (action, params) = extract_form_params(lucky_page, 'number_choice', "" );
                    survey_page = submit_page(domain+action,params);
                else:
                    survey_page = lucky_page;

                (action, params) = extract_form_params(survey_page, 'question_blocks', "(?!=[^>]*yes)" );
                win_page = submit_page(domain+action,params);

                open_mystery_box( win_page, id );

                if domain != "http://www.win4now.co.uk":
                    extract_win_message( win_page, comp_url );

                count = count - 1;
                if count == 0:  print "END: 50 Entries POSTED"; break;


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "win4now":
        domain         = "http://www.win4now.co.uk"
        list_prefix    = "/prize-draws-not-entered"
        mystery_prefix = "/mystery-envelope"
        logins = ["2HT2BBNMTK6001F"]
        cats = [""]
        spider()
    else:
        domain         = "http://www.instantwin4now.co.uk"
        list_prefix    = "/comps"
        mystery_prefix = "/mystery-box"

        # All Logins Revoked - Wait a couple of weeks and regregister only a few accounts
        logins = [
#            "3WP2B9Q4T3L00CF",
#            "D512B9V4TP9001D",
#            "FDL2B6NMTND001B",
#            "L4B2BZ44T4D00BV",
#            "NH92B0LLTKG00CF",
#            "R042BFB4TS700CX",
#            "RQV2BT64TZT00BZ",
#            "V7R2B1KMTFW00CD",
#            "VKC2BXS4TDG00C2",
#            "ZX6GB0H1T1200BL",
#            "PB1GBCH1T7D00BH",
#            "04GGBCQ1TTM00C4",
#            "VZMGBCK1T8100BW",
#            "04HGB1L1T1X00BQ"
        ]
        cats = ["cash","cash","cash","cash","motoring","motoring","holidays","lifestyle","electrical"];

        spider()
        
