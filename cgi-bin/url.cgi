#!/Perl64/bin/perl -w
use strict;
use warnings;
use WWW::Mechanize;
use HTTP::Cookies;



my $mech = WWW::Mechanize->new();
my $url = "https://www.macmillaneducationeverywhere.com/login";

#$mech->agent('User-Agent=Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5');
$mech->cookie_jar(HTTP::Cookies->new(autosave => 1));
#$mech->cookie_jar->set_cookie(0,'cookiename', 'value','/','google.com',80,0,0,86400,0);

$mech->get($url);

$mech->submit_form(  
    with_fields  => {
        username => "",
        password => ""
    },
);
#$mech->click_button( number => 4 );

#print $mech->uri();
#print $mech->response() ->content();
#print $mech->response();
#print $mech->text();

my $res = $mech->response()->as_string("\n");

print "Content-type: text/html\n\n";
print "<html><h1>$res</h1></html>\n";

#print "Location: $res\n\n";
#print $mech->content(base_href => $mech->base());



