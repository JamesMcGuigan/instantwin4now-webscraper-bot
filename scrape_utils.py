#! /usr/bin/python
import sys
import random
import re
import urllib
import urllib2
import os

def unique(seq, idfun=None):
    """ http://www.peterbe.com/plog/uniqifiers-benchmark """
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result

def latin1_to_ascii (unicrap):
    """This replaces UNICODE Latin-1 characters with
    something equivalent in 7-bit ASCII. All characters in the standard
    7-bit ASCII range are preserved. In the 8th bit range all the Latin-1
    accented letters are stripped of their accents. Most symbol characters
    are converted to something meaninful. Anything not converted is deleted.
    """
    xlate={ 0xc0:'A', 0xc1:'A', 0xc2:'A', 0xc3:'A', 0xc4:'A', 0xc5:'A', 0xc6:'Ae', 0xc7:'C', 0xc8:'E', 0xc9:'E', 0xca:'E', 0xcb:'E', 0xcc:'I', 0xcd:'I', 0xce:'I', 0xcf:'I', 0xd0:'Th', 0xd1:'N', 0xd2:'O', 0xd3:'O', 0xd4:'O', 0xd5:'O', 0xd6:'O', 0xd8:'O',
            0xd9:'U', 0xda:'U', 0xdb:'U', 0xdc:'U', 0xdd:'Y', 0xde:'th', 0xdf:'ss', 0xe0:'a', 0xe1:'a', 0xe2:'a', 0xe3:'a', 0xe4:'a', 0xe5:'a', 0xe6:'ae', 0xe7:'c', 0xe8:'e', 0xe9:'e', 0xea:'e', 0xeb:'e', 0xec:'i', 0xed:'i', 0xee:'i', 0xef:'i',
            0xf0:'th', 0xf1:'n', 0xf2:'o', 0xf3:'o', 0xf4:'o', 0xf5:'o', 0xf6:'o', 0xf8:'o', 0xf9:'u', 0xfa:'u', 0xfb:'u', 0xfc:'u', 0xfd:'y', 0xfe:'th', 0xff:'y', 0xa1:'!', 0xa2:'{cent}', 0xa3:'{pound}', 0xa4:'{currency}', 0xa5:'{yen}', 0xa6:'|', 0xa7:'{section}', 0xa8:'{umlaut}',
            0xa9:'{C}', 0xaa:'{^a}', 0xab:'<<', 0xac:'{not}', 0xad:'-', 0xae:'{R}', 0xaf:'_', 0xb0:'{degrees}', 0xb1:'{+/-}', 0xb2:'{^2}', 0xb3:'{^3}', 0xb4:"'", 0xb5:'{micro}', 0xb6:'{paragraph}', 0xb7:'*', 0xb8:'{cedilla}', 0xb9:'{^1}', 0xba:'{^o}', 0xbb:'>>',
            0xbc:'{1/4}', 0xbd:'{1/2}', 0xbe:'{3/4}', 0xbf:'?', 0xd7:'*', 0xf7:'/' }

    r = ''
    for i in unicrap:
        if xlate.has_key(ord(i)):
            r += xlate[ord(i)]
        elif ord(i) >= 0x80:
            pass
        else:
            r += i
    return r


def get_url( url ):
    opener = urllib2.build_opener()
    request = urllib2.Request(url);
    request.add_header("User-Agent", "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2) Gecko/20091218 Firefox 3.6b5");
    print "GET:  ", request.get_full_url();
    html = opener.open(request).read();
    html = latin1_to_ascii(html)
    return html;

def submit_page( action, params ):
    if action == "": return "";

    opener = urllib2.build_opener()
    data    = urllib.urlencode(params);
    request = urllib2.Request( action, data );
    request.add_header("User-Agent", "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2) Gecko/20091218 Firefox 3.6b5");
    print "POST: ", request.get_full_url(), params;
    html = opener.open(request).read();
    html = latin1_to_ascii(html)
    return html;


def extract_form_params( html, name, input_filter ):
    forms = re.findall('<form[^>]*name="'+name+'"[^>]*>.*?</form>', html, re.S | re.I );
    if len(forms) == 0: return ("", "");

    action = re.findall('action="([^>"]*)"', forms[0], re.DOTALL | re.IGNORECASE )[0];
    inputs = re.findall('<input[^>]*>'+input_filter, forms[0], re.DOTALL | re.IGNORECASE );
    params = {};
    if len(inputs) == 0:
        print html;
        print "REGEXP ERROR"
        exit();

    for input in inputs:
        try:
            name  = re.findall('name="([^>"]*)"', input, re.IGNORECASE)[0];
            value = re.findall('value="([^>"]*)"', input, re.IGNORECASE);
            value = value[0] if len(value) > 0 else "on";
            params[name] = value;
        except:
            print "REGEXP ERROR: ", input

    return action, params;

def email_self( subject, body ):
    SENDMAIL = "/usr/sbin/sendmail" # sendmail location

    FROM = "jamie@localhost"
    TO  = ["jamie@localhost"]
    SUBJECT = subject
    TEXT = body

    message = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    # Send the mail
    p = os.popen("%s -t -i jamie@localhost" % SENDMAIL, "w")
    p.write(message)
    status = p.close()
    if status:
        print "Sendmail exit status", status
