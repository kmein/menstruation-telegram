# generated using pypi2nix tool (version: 1.8.1)
# See more at: https://github.com/garbas/pypi2nix
#
# COMMAND:
#   pypi2nix -V 3.6 -e gdom -E libxml2 -E libxslt
#

{ pkgs ? import <nixpkgs> {},
  overrides ? ({ pkgs, python }: self: super: {})
}:

let

  inherit (pkgs) makeWrapper;
  inherit (pkgs.stdenv.lib) fix' extends inNixShell;

  pythonPackages =
  import "${toString pkgs.path}/pkgs/top-level/python-packages.nix" {
    inherit pkgs;
    inherit (pkgs) stdenv;
    python = pkgs.python36;
    # patching pip so it does not try to remove files when running nix-shell
    overrides =
      self: super: {
        bootstrapped-pip = super.bootstrapped-pip.overrideDerivation (old: {
          patchPhase = old.patchPhase + ''
            if [ -e $out/${pkgs.python36.sitePackages}/pip/req/req_install.py ]; then
              sed -i \
                -e "s|paths_to_remove.remove(auto_confirm)|#paths_to_remove.remove(auto_confirm)|"  \
                -e "s|self.uninstalled = paths_to_remove|#self.uninstalled = paths_to_remove|"  \
                $out/${pkgs.python36.sitePackages}/pip/req/req_install.py
            fi
          '';
        });
      };
  };

  commonBuildInputs = with pkgs; [ libxml2 libxslt ];
  commonDoCheck = false;

  withPackages = pkgs':
    let
      pkgs = builtins.removeAttrs pkgs' ["__unfix__"];
      interpreterWithPackages = selectPkgsFn: pythonPackages.buildPythonPackage {
        name = "python36-interpreter";
        buildInputs = [ makeWrapper ] ++ (selectPkgsFn pkgs);
        buildCommand = ''
          mkdir -p $out/bin
          ln -s ${pythonPackages.python.interpreter} \
              $out/bin/${pythonPackages.python.executable}
          for dep in ${builtins.concatStringsSep " "
              (selectPkgsFn pkgs)}; do
            if [ -d "$dep/bin" ]; then
              for prog in "$dep/bin/"*; do
                if [ -x "$prog" ] && [ -f "$prog" ]; then
                  ln -s $prog $out/bin/`basename $prog`
                fi
              done
            fi
          done
          for prog in "$out/bin/"*; do
            wrapProgram "$prog" --prefix PYTHONPATH : "$PYTHONPATH"
          done
          pushd $out/bin
          ln -s ${pythonPackages.python.executable} python
          ln -s ${pythonPackages.python.executable} \
              python3
          popd
        '';
        passthru.interpreter = pythonPackages.python;
      };

      interpreter = interpreterWithPackages builtins.attrValues;
    in {
      __old = pythonPackages;
      inherit interpreter;
      inherit interpreterWithPackages;
      mkDerivation = pythonPackages.buildPythonPackage;
      packages = pkgs;
      overrideDerivation = drv: f:
        pythonPackages.buildPythonPackage (
          drv.drvAttrs // f drv.drvAttrs // { meta = drv.meta; }
        );
      withPackages = pkgs'':
        withPackages (pkgs // pkgs'');
    };

  python = withPackages {};

  generated = self: {
    "Click" = python.mkDerivation {
      name = "Click-7.0";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/f8/5c/f60e9d8a1e77005f664b76ff8aeaee5bc05d0a91798afd7f53fc998dbc47/Click-7.0.tar.gz"; sha256 = "5b94b49521f6456670fdb30cd82a4eca9412788a93fa6dd6df72c94d5a8ff2d7"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://palletsprojects.com/p/click/";
        license = licenses.bsdOriginal;
        description = "Composable command line interface toolkit";
      };
    };

    "Flask" = python.mkDerivation {
      name = "Flask-1.0.2";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/4b/12/c1fbf4971fda0e4de05565694c9f0c92646223cff53f15b6eb248a310a62/Flask-1.0.2.tar.gz"; sha256 = "2271c0070dbcb5275fad4a82e29f23ab92682dc45f9dfbc22c02ba9b9322ce48"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."Click"
      self."Jinja2"
      self."Werkzeug"
      self."itsdangerous"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://www.palletsprojects.com/p/flask/";
        license = licenses.bsdOriginal;
        description = "A simple framework for building complex web applications.";
      };
    };

    "Flask-GraphQL" = python.mkDerivation {
      name = "Flask-GraphQL-1.4.1";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/d5/3d/54698202bb63f134e68b1891208cf80021195c9a5d728fd76d21dc8a86c0/Flask-GraphQL-1.4.1.tar.gz"; sha256 = "84be72d6b0f81dc0fb9d2177fc0222a885f85d84da4ce755972ca16be413b7bc"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."Flask"
      self."graphql-core"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/graphql-python/flask-graphql";
        license = licenses.mit;
        description = "Adds GraphQL support to your Flask application";
      };
    };

    "Jinja2" = python.mkDerivation {
      name = "Jinja2-2.10";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/56/e6/332789f295cf22308386cf5bbd1f4e00ed11484299c5d7383378cf48ba47/Jinja2-2.10.tar.gz"; sha256 = "f84be1bb0040caca4cea721fcbbbbd61f9be9464ca236387158b0feea01914a4"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."MarkupSafe"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://jinja.pocoo.org/";
        license = licenses.bsdOriginal;
        description = "A small but fast and easy to use stand-alone template engine written in pure python.";
      };
    };

    "MarkupSafe" = python.mkDerivation {
      name = "MarkupSafe-1.0";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/4d/de/32d741db316d8fdb7680822dd37001ef7a448255de9699ab4bfcbdf4172b/MarkupSafe-1.0.tar.gz"; sha256 = "a6be69091dac236ea9c6bc7d012beab42010fa914c459791d627dad4910eb665"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://github.com/pallets/markupsafe";
        license = licenses.bsdOriginal;
        description = "Implements a XML/HTML/XHTML Markup safe string for Python";
      };
    };

    "Rx" = python.mkDerivation {
      name = "Rx-1.6.1";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/25/d7/9bc30242d9af6a9e9bf65b007c56e17b7dc9c13f86e440b885969b3bbdcf/Rx-1.6.1.tar.gz"; sha256 = "13a1d8d9e252625c173dc795471e614eadfe1cf40ffc684e08b8fff0d9748c23"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://reactivex.io";
        license = "License :: OSI Approved :: Apache Software License";
        description = "Reactive Extensions (Rx) for Python";
      };
    };

    "Werkzeug" = python.mkDerivation {
      name = "Werkzeug-0.14.1";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/9f/08/a3bb1c045ec602dc680906fc0261c267bed6b3bb4609430aff92c3888ec8/Werkzeug-0.14.1.tar.gz"; sha256 = "c3fd7a7d41976d9f44db327260e263132466836cef6f91512889ed60ad26557c"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://www.palletsprojects.org/p/werkzeug/";
        license = licenses.bsdOriginal;
        description = "The comprehensive WSGI web application library.";
      };
    };

    "cssselect" = python.mkDerivation {
      name = "cssselect-1.0.3";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/52/ea/f31e1d2e9eb130fda2a631e22eac369dc644e8807345fbed5113f2d6f92b/cssselect-1.0.3.tar.gz"; sha256 = "066d8bc5229af09617e24b3ca4d52f1f9092d9e061931f4184cd572885c23204"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/scrapy/cssselect";
        license = licenses.bsdOriginal;
        description = "cssselect parses CSS3 Selectors and translates them to XPath 1.0";
      };
    };

    "gdom" = python.mkDerivation {
      name = "gdom-1.0.0";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/76/79/1ccbf38c32576dbb29efdc35819f96a99768266cdf6dc1586aef0e9fbe73/gdom-1.0.0.tar.gz"; sha256 = "66b092ea846cf9b462d7fad23181cbc07603e43b662d39d7a2dacfe502af56ac"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."Flask-GraphQL"
      self."graphene"
      self."pyquery"
      self."requests"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://github.com/syrusakbary/gdom";
        license = licenses.mit;
        description = "DOM Traversing and Scraping using GraphQL";
      };
    };

    "graphene" = python.mkDerivation {
      name = "graphene-2.0.1";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/99/b4/7fc49f6728fcdbae54f97aaa8422fffd1c4baf576142105ddfda731f7615/graphene-2.0.1.tar.gz"; sha256 = "0763563fdccb6817311f15d0f0a4d4fe820a46cbe5de022076f95cd99413fd0f"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."graphql-core"
      self."graphql-relay"
      self."promise"
      self."six"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/graphql-python/graphene";
        license = licenses.mit;
        description = "GraphQL Framework for Python";
      };
    };

    "graphql-core" = python.mkDerivation {
      name = "graphql-core-2.1";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/d8/b7/7b16d70ca5f12c3877b098a2b6024813fb7a168b4c163fc425b123f5d48a/graphql-core-2.1.tar.gz"; sha256 = "889e869be5574d02af77baf1f30b5db9ca2959f1c9f5be7b2863ead5a3ec6181"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."Rx"
      self."promise"
      self."six"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/graphql-python/graphql-core";
        license = licenses.mit;
        description = "GraphQL implementation for Python";
      };
    };

    "graphql-relay" = python.mkDerivation {
      name = "graphql-relay-0.4.5";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/5e/b0/b91fadc180544fc9e3c156d7049561fd5f1e2211d26fd29033548fd50934/graphql-relay-0.4.5.tar.gz"; sha256 = "2716b7245d97091af21abf096fabafac576905096d21ba7118fba722596f65db"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."graphql-core"
      self."promise"
      self."six"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/graphql-python/graphql-relay-py";
        license = licenses.mit;
        description = "Relay implementation for Python";
      };
    };

    "itsdangerous" = python.mkDerivation {
      name = "itsdangerous-0.24";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/dc/b4/a60bcdba945c00f6d608d8975131ab3f25b22f2bcfe1dab221165194b2d4/itsdangerous-0.24.tar.gz"; sha256 = "cbb3fcf8d3e33df861709ecaf89d9e6629cff0a217bc2848f1b41cd30d360519"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://github.com/mitsuhiko/itsdangerous";
        license = licenses.bsdOriginal;
        description = "Various helpers to pass trusted data to untrusted environments and back.";
      };
    };

    /*
    "jq" = python.mkDerivation {
      name = "jq-0.1.6";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/82/0c/bf3f544f850cef19f4468bea93e4d0aa908e0d8c601609ba1ed561b42c79/jq-0.1.6.tar.gz"; sha256 = "34bdf9f9e49e522e1790afc03f3584c6b57329215ea0567fb2157867d6d6f602"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = with pkgs; [ autoconf automake libtool ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://github.com/mwilliamson/jq.py";
        license = licenses.bsdOriginal;
        description = "jq is a lightweight and flexible JSON processor.";
      };
    };
    */

    "lxml" = python.mkDerivation {
      name = "lxml-4.2.5";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/4b/20/ddf5eb3bd5c57582d2b4652b4bbcf8da301bdfe5d805cb94e805f4d7464d/lxml-4.2.5.tar.gz"; sha256 = "36720698c29e7a9626a0dc802ef8885f8f0239bfd1689628ecd459a061f2807f"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."cssselect"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://lxml.de/";
        license = licenses.bsdOriginal;
        description = "Powerful and Pythonic XML processing library combining libxml2/libxslt with the ElementTree API.";
      };
    };

    "promise" = python.mkDerivation {
      name = "promise-2.2.1";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/5a/81/221d09d90176fd90aed4b530e31b8fedf207385767c06d1d46c550c5e418/promise-2.2.1.tar.gz"; sha256 = "348f5f6c3edd4fd47c9cd65aed03ac1b31136d375aa63871a57d3e444c85655c"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."six"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/syrusakbary/promise";
        license = licenses.mit;
        description = "Promises/A+ implementation for Python";
      };
    };

    "pyquery" = python.mkDerivation {
      name = "pyquery-1.3.0";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/f6/0e/f01ff19cd0dd74f60431db77dbf4b0b16ee9dff21f96d6595af64afe2bf1/pyquery-1.3.0.tar.gz"; sha256 = "5821ffd02301db701cb30f2483ab96774c2b6b70530f79a44645f49dc5053ab8"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."cssselect"
      self."lxml"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/gawel/pyquery";
        license = licenses.bsdOriginal;
        description = "A jquery-like library for python";
      };
    };

    "requests" = python.mkDerivation {
      name = "requests-2.9.1";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/f9/6d/07c44fb1ebe04d069459a189e7dab9e4abfe9432adcd4477367c25332748/requests-2.9.1.tar.gz"; sha256 = "c577815dd00f1394203fc44eb979724b098f88264a9ef898ee45b8e5e9cf587f"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://python-requests.org";
        license = licenses.asl20;
        description = "Python HTTP for Humans.";
      };
    };

    "six" = python.mkDerivation {
      name = "six-1.11.0";
      src = pkgs.fetchurl { url = "https://files.pythonhosted.org/packages/16/d8/bc6316cf98419719bd59c91742194c111b6f2e85abac88e496adefaf7afe/six-1.11.0.tar.gz"; sha256 = "70e8a77beed4562e7f14fe23a786b54f6296e34344c23bc42f07b15018ff98e9"; };
      doCheck = commonDoCheck;
      checkPhase = "";
      installCheckPhase = "";
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://pypi.python.org/pypi/six/";
        license = licenses.mit;
        description = "Python 2 and 3 compatibility utilities";
      };
    };
  };
  localOverridesFile = ./requirements_override.nix;
  localOverrides = import localOverridesFile { inherit pkgs python; };
  commonOverrides = [

  ];
  paramOverrides = [
    (overrides { inherit pkgs python; })
  ];
  allOverrides =
    (if (builtins.pathExists localOverridesFile)
     then [localOverrides] else [] ) ++ commonOverrides ++ paramOverrides;

in python.withPackages
   (fix' (pkgs.lib.fold
            extends
            generated
            allOverrides
         )
   )
