#!/Perl64/bin/perl -w
use strict;
use CGI::Session;
#use CGI::Carp;

print "Content-type: text/html\n\n";

CGI::Session->find("driver:mysql", \&f_delete, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();
print "Операция выполнена<BR>";

sub f_delete {
        my ($session)=@_;
        next if $session->is_empty();
        if (($session->ctime()+86400)<time()) {
        $session->delete();
}

}
__END__
