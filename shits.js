    const brutekey = (encodedString) => {
      const results = [];
      for (let i = 0; i <= 999; i++) {
        const key = i.toString();
        const decoded = encodedString.split('').map((char, index) => {
          return String.fromCharCode(
            char.charCodeAt(0) ^ key.charCodeAt(index % key.length)
          );
        }).join('');
        const check = decoded.split('').every(char => {
          const code = char.charCodeAt(0);
          if (char === '@' || char === '|' || char === '~' || char === '`' || char === '<' || char === '>') {
            return false;
          }
          return true;
        });
        if (check) {
          results.push({
            key: i,
            decoded: decoded
          });
        }
      }
      return results;
    };

    console.log(brutekey("|yqsyRp~zV[IY[Qv\tO\u0001ry`u~pqwrqi\tquxyzrWsrqitqAp_d{pD~w\\n{AyYA\u0013\\\bQ{\u0007~di\bt\b\u0001rvm\u001e^PAD\u000e\u001egnDgP@E@\t\u0003\u000e\u0001AI]wrKw\u000ecAVrHOv\u0003{wBO\b{IdXn{\u0007wt^[UYb\tx|fH\u000b\u001awrR}tfWP}x\u000f_a\u000b|CNEG^[aDHba\u001f}\\\u0007\n\u001aB{\tVnRXZv[j\u0004\u0002}\u0004sk}yKrEOK}u\u0004u~|uz|\u0006P~Huf\u001fU{Qt[uBI\u0006PszzsCWEaz\u001e\u001bvicryr~ui\u000bG\u0001OVGO\bZ\nsjNiC\nGR}}cMe\u0002Yhrna\u0007ba\u0005\u000bCQ\u000fKi]Gfi|^m\u0004\u0007\u0013\\\u0002vU]\u0013\u001eHC\u001b\u000fiahxfmIsWDJhzswbH\u000f\u001aWQAeKRQqXg~\bLiulHEMKIPvGv~@\fGIlSxwUrUIas\u001et`\u0002}\u0000V\t\u0017pGI@\u0003mvvI\u0006SNKaquqipr"))