#!/usr/bin/perl -w

use Time::HiRes qw(gettimeofday tv_interval);
my $t0 = [gettimeofday];

use lib qw(/home/sulciphur/lib/perl5/lib/x86_64-linux-gnu-thread-multi /home/sulciphur/lib/perl5/lib);

use Dough::CGI;
use Dough::Log;
use Dough::Config;

my $log = Dough::Log->instance();
$log->sepWStr($ENV{REMOTE_ADDR});

my $cgi = Dough::CGI->new();

if ($cgi) {
    if ($cgi->processQuery()) {
        $log->log("ERROR:\t\t" . $cgi->{resp}->{Error}), unless ($cgi->sendResponseAsJSON());
    }
    else {
        $log->log("No response object.");
        print "Content-type: text/plain\n\nError.";
    }
}
else {
    print "Location: $k_placeholderURL\n\n";
}

$log->sepWStr(tv_interval($t0) . "s");
