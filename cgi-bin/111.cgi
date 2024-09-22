#!/Perl64/bin/perl -w
print "Content-type: text/html\n\n";
print "<html><head><title>Installed Perl Modules</title></head><body><table width=\"300px\" border=1><td><tr><td>Module</td> <td>Version</td>";
use ExtUtils::Installed;
my $instmod = ExtUtils::Installed->new();
foreach my $module ($instmod->modules())
{ my $version = $instmod->version($module) || "-"; print "<tr><td>$module</td> <td>$version</td></tr> \r\n"; }
print "</table></body></html>";