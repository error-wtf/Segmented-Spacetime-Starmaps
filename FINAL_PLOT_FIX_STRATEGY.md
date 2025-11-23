# FINALE Plot-Fix Strategie

## Problem-Analyse aus Screenshots:

1. **g₁/g₂ Plot**: Achsen zeigen 10^15 statt parsecs
   - Root cause: Verwendet Meter statt PC
   
2. **Time Dilation**: Crossover bei r*/r_s = 6.000 statt 1.387
   - Root cause: Falsche gamma_seg oder D-Berechnung

3. **Radial Stretch**: Leer
   - Root cause: Daten außerhalb des Plot-Bereichs

4. **Combined**: Plot da aber keine Daten
   - Root cause: Ähnlich wie Radial Stretch

## PAPER-RESTORED Mathematik (KORREKT):

### Von generate_validation_plots_compact.py (Zeile 26-29):
```python
def gamma_seg(r, r_s, a=0.12, rc=1.9): 
    return 1 - a*np.exp(-(r/(rc*r_s))**2)
    
def D(r, r_s, a=0.12, rc=1.9): 
    return 1/(1 + (1-gamma_seg(r,r_s,a,rc)))
    
def A_SSZ(r, M): 
    r_s=2*G*M/C**2
    return D(r,r_s)*(1-r_s/r)
```

### Von generate_local_plots.py (Zeile 164-166):
```python
def gamma_seg(r):
    r_norm = r / r_s
    return 1.0 - alpha * np.exp(-(r_norm / r_c)**2)
```

**DAS SIND DIE GLEICHEN!** (r/(rc*r_s)) == ((r/r_s)/rc)

## Strategie:

1. Nehme 1:1 die Funktionen von generate_validation_plots_compact.py
2. Checke die Plot-Bereiche (r_range) ob sie stimmen
3. Checke ob Daten generiert werden
4. Fixe Achsen-Labels

## Next Steps:

1. Copy EXACT functions from PAPER-RESTORED
2. Test each plot individually
3. Fix ranges if needed
