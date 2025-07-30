
## Examples

* Convert glyco nomenclature of a sphingolipid into SMILES with defined n-acyl and sphingoid base

```bash
glycosphingotool convert "NeuAcalpha2-3Galbeta1-4GlcCer" --nacyl CCC --sphingoid "[C@H](O)/C=C/CC"
```
* Generate synthesis reactions for glyco nomenclature of a sphingolipid, generate reactions SMILES, RInChI and Web-RInChIKeys with defined n-acyl and sphingoid base

```bash
glycosphingotool generate "NeuAcalpha2-3Galbeta1-4GlcCer" --nacyl CCC --sphingoid "[C@H](O)/C=C/CC" --output-folder "NeuAcalpha2-3Galbeta1-4GlcCer"
```

* Process all the Excel file downloaded from SphingoMAP (the original link is currently broken at the original resource)

```bash
glycosphingotool process-all --output-folder 'results_SphingoMAP' --nacyl CCC --sphingoid "[C@H](O)/C=C/CCCCCC"
```

The source SphingomapkeyV1.4.xls can be found in src/glycosphingotool/assets