package Dough::CGI::Process;

use Exporter qw(import);

use Dough::CGI;

@EXPORT = qw(queryWithAttribute);

sub queryWithAttributes {
	my $cgi = shift;
	print "CGI obj: $cgi\n";

	return {};
}

1;
