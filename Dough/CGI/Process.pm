package Dough::CGI::Process;

use Exporter qw(import);

use Dough::Config;
use Dough::CGI;
use Dough::SDB;

@EXPORT = qw(qwa);

sub qwa {
    my ($cgi) = @_;
	print STDERR "CGI obj: $cgi\n";

    my $phid = $cgi->{phid};
    my $dom = $cgi->{q}->param('d');
    my $qDom = ($dom && $dom eq 'u' ? $k_awsUserDom : $k_awsTADom);

    my $qStr = "['deviceID' = '$phid']";
    my $rHash = { DomainName => $qDom, QueryExpression => $qStr };
    
    my $_r = $cgi->{sdb}->queryWithAttrs($rHash);
    $cgi->{l}->log("QWA ret: $_r");

    return {};
}

1;
