# Data info
Este archivo es para guardar información relevante de los datos del HCP 1200, en particular, información para la tesis.
| Code | Sex | Age | Code | Sex | Age | Code | Sex | Age |
| :--- | :---: | :---: | :--- | :---: | :---: | :--- | :---: | :---: |
| 105923 | F | 31–35 | 191033 | F | 26–30 | 581450 | M | 22–25 |
| 106521 | F | 26–30 | 191437 | F | 31–35 | 599671 | M | 26–30 |
| 108323 | F | 26–30 | 192641 | F | 31–35 | 601127 | M | 22–25 |
| 109123 | M | 31–35 | 198653 | M | 22–25 | 660951 | F | 26–30 |
| 113922 | M | 31–35 | 204521 | F | 31–35 | 662551 | M | 26–30 |
| 116726 | M | 26–30 | 205119 | M | 31–35 | 667056 | M | 22–25 |
| 133019 | F | 26–30 | 212318 | F | 31–35 | 679770 | M | 26–30 |
| 140117 | F | 26–30 | 212823 | M | 22–25 | 680957 | F | 26–30 |
| 156334 | F | 26–30 | 255639 | F | 26–30 | 706040 | F | 22–25 |
| 162026 | F | 31–35 | 257845 | M | 26–30 | 707749 | M | 31–35 |
| 162935 | M | 22–25 | 283543 | M | 22–25 | 725751 | M | 26–30 |
| 164636 | M | 22–25 | 293748 | F | 31–35 | 735148 | M | 22–25 |
| 169040 | M | 22–25 | 353740 | M | 22–25 | 783462 | M | 22–25 |
| 175237 | F | 31–35 | 358144 | F | 26–30 | 814649 | M | 26–30 |
| 177746 | F | 26–30 | 406836 | F | 31–35 | 891667 | M | 26–30 |
| 185442 | M | 22–25 | 568963 | F | 31–35 | 898176 | M | 31–35 |

## Sujetos
ID de 48 sujetos seleccionados
```python
sujetos = ["105923", "106521", "108323", "109123", "113922", "116726", "133019", "140117", "156334", "162026", "162935", "164636", "169040", "175237", "177746", "185442", "191033", "191437", "192641", "198653", "204521", "205119", "212318", "212823", "255639", "257845", "283543", "293748", "353740", "358144", "406836", "568963", "581450", "599671", "601127", "660951", "662551", "667056", "679770", "680957", "706040", "707749", "725751", "735148", "783462", "814649", "891667", "898176"]

```

Lista de los canales MEG que aparecen en los 48 sujetos 
```
canales_meg = ['A56', 'A215', 'A178', 'A125', 'A81', 'A130', 'A207', 'A200', 'A180', 'A49', 'A118', 'A138', 'A181', 'A195', 'A131', 'A114', 'A66', 'A221', 'A30', 'A141', 'A167', 'A166', 'A97', 'A44', 'A216', 'A40', 'A69', 'A192', 'A144', 'A206', 'A12', 'A25', 'A224', 'A46', 'A239', 'A65', 'A168', 'A31', 'A101', 'A117', 'A80', 'A14', 'A194', 'A86', 'A57', 'A54', 'A11', 'A219', 'A161', 'A109', 'A234', 'A51', 'A135', 'A199', 'A208', 'A3', 'A151', 'A92', 'A93', 'A72', 'A115', 'A110', 'A78', 'A136', 'A107', 'A10', 'A142', 'A185', 'A209', 'A133', 'A82', 'A58', 'A84', 'A95', 'A100', 'A140', 'A48', 'A132', 'A89', 'A13', 'A7', 'A134', 'A83', 'A127', 'A71', 'A169', 'A186', 'A184', 'A106', 'A42', 'A171', 'A26', 'A105', 'A202', 'A35', 'A174', 'A96', 'A158', 'A67', 'A108', 'A213', 'A24', 'A218', 'A79', 'A23', 'A149', 'A160', 'A242', 'A39', 'A32', 'A191', 'A156', 'A179', 'A21', 'A47', 'A16', 'A64', 'A55', 'A98', 'A163', 'A165', 'A139', 'A233', 'A4', 'A22', 'A43', 'A77', 'A85', 'A76', 'A50', 'A9', 'A29', 'A137', 'A143', 'A204', 'A99', 'A53', 'A240', 'A188', 'A75', 'A28', 'A33', 'A203', 'A34', 'A74', 'A170', 'A103', 'A91', 'A27', 'A220', 'A154', 'A164', 'A113']
```

## Información de los archivos trialinfo.mat
| Experimento | Grupo de Datos | Evento Definitorio |
| :--- | :--- | :--- |
| Tarea Motora | TFLA | Inicio de la cruz parpadeante que indica al sujeto realizar el movimiento con la mano o el pie. |
| Tarea Motora | TEMG | Inicio de la señal EMG de los músculos registrados de la mano o el pie. |
| Memoria de Trabajo | TIM | Inicio de una imagen que el sujeto debe emparejar o no con la imagen objetivo. |
| Memoria de Trabajo | TRESP | Inicio de la pulsación del botón por parte del sujeto. |

### Working Memory: TIM & TRESP
En este caso las variables son las mismas

| Número de Columna | Descripción | Notas |
| :--- | :--- | :--- |
| 1 | Número de Ejecución (Run) | El número de ejecución se decodifica de los activadores de E-Prime. En muchos casos, este activador inicial no está disponible; en ese caso, se establece en 1 y el usuario debe inferirlo del nombre del escaneo. |
| 2 | Número de Bloque | Número de bloque dentro de la ejecución. |
| 3 | NaN (Not a Number) | Esta columna está reservada para el ID de la imagen, el cual no está codificado en los valores del activador. Aún no está implementado. |
| 4 | Tipo de Imagen (ImageType) | 1: Cara, 2: Herramientas, 0: Fijación. |
| 5 | Tipo de Memoria (memoryType) | 1: 0-Back, 2: 2-Back. |
| 6 | Tipo de Objetivo (targetType) | 1: Objetivo (target), 2: No objetivo, 3: Señuelo (lure). |
| 7 | Inicio del activador del ensayo | Muestra (sample) de inicio del activador del ensayo. |
| 8 | Fin del activador del ensayo | Muestra (sample) de fin del activador del ensayo. |
| 9 | Secuencia de imagen | Secuencia de la imagen dentro del bloque. |
| 10 | isPressed | 0: El sujeto no presionó ningún botón de respuesta; 1: El sujeto presionó un botón de respuesta. |
| 11 | isPressedLate | 1: Si el sujeto respondió después de mostrarse la imagen (máx. 2 seg), pero antes del siguiente ensayo; 0: Si respondió dentro del tiempo de presentación; NaN: Otro caso. |
| 12 | isDoubleResponse | 1: Si el sujeto presionó dos botones en el mismo ensayo; 0: El usuario NO presionó dos botones. |
| 13 | pressedCode | Código del botón presionado (Si no se presionó, NaN). |
| 14 | isCorrect | 1: Si respondió "objetivo" ante un objetivo real o "no objetivo" ante uno real; 0: Lo opuesto; NaN: Cuando no respondió o presionó dos botones. |
| 15 | isLureAsCorrect | 1: Si respondió "objetivo" ante un señuelo (lure) de un objetivo real; 0: En todos los demás casos con respuesta; NaN: Sin respuesta o con dos botones. |
| 16 | respTime | Tiempo desde el inicio de la imagen hasta la respuesta (segundos). |
| 17 | respDuration | Duración de la pulsación del botón en segundos. |
| 18 | isFirstInBlock | Indica si es el primero en el bloque. |
| 19 | isLastInBlock | Indica si es el último en el bloque. |
| 20 | Ensayo prev: Run Number | Igual que 1, pero para el ensayo anterior. |
| 21 | Ensayo prev: Block number | Igual que 2, pero para el ensayo anterior. |
| 22 | Ensayo prev: Nan | Igual que 3, pero para el ensayo anterior. |
| 23 | Bloque prev: ImageType | Igual que 4, pero para el bloque anterior. |
| 24 | Bloque prev: memoryType | Igual que 5, pero para el bloque anterior. |
| 25 | Ensayo prev: targetType | Igual que 6, pero para el bloque anterior. |
| 26 | Ensayo prev: Start Sample | Igual que 7, pero para el bloque anterior. |
| 27 | Ensayo prev: End Sample | Igual que 8, pero para el bloque anterior. |
| 28 | Ensayo prev: Sequence | Igual que 9, pero para el bloque anterior. |
| 29 | Ensayo prev: isPressed | Igual que 10, pero para el bloque anterior. |
| 30 | Ensayo prev: isPressedLate | Igual que 11, pero para el bloque anterior. |
| 31 | Ensayo prev: isDoubleResponse | Igual que 12, pero para el bloque anterior. |
| 32 | Ensayo prev: pressedCode | Igual que 13, pero para el bloque anterior. |
| 33 | Ensayo prev: isCorrect | Igual que 14, pero para el bloque anterior. |
| 34 | Ensayo prev: isLureAsCorrect | Igual que 15, pero para el bloque anterior. |
| 35 | Ensayo prev: respTime | Igual que 16, pero para el bloque anterior. |
| 36 | Ensayo prev: respDuration | Igual que 17, pero para el bloque anterior. |
| 37 | Ensayo prev: isFirstInBlock | Igual que 18, pero para el bloque anterior. |
| 38 | Ensayo prev: isLastInBlock | Igual que 19, pero para el bloque anterior. |
| 39 | Press during onset | Indica si se presionó el botón durante el inicio del estímulo. |
| 40 | has trial NANs | Indica si hay segmentos en el ensayo donde los datos han sido reemplazados por NaNs (usado en ensayos de longitud variable o largos).|

### MotorTask: TEMG
| Número de columna | Descripción | Notas |
| :--- | :--- | :--- |
| 1 | Número de Bloque dentro de la Ejecución | |
| 2 | Código de Estímulo del Bloque | 1 - Mano Izquierda, 2 - Pie Izquierdo, 4 - Mano Derecha, 5 - Pie Derecho, 6 - Fijación. |
| 3 | Índice del Ensayo en el Bloque | Para el grupo TEMG, esto se deriva buscando el inicio de la cruz parpadeante justo antes del inicio de la EMG. |
| 4 | Muestra de Inicio de EMG del Ensayo | |
| 5 | Código de Estímulo del Bloque anterior | |
| 6 | Tiempo desde el inicio de la EMG hasta la Cruz Parpadeante anterior | |
| 7 | has trial NANs (valores No Numéricos) | Esta bandera se utiliza para indicar si hay segmentos de datos en el ensayo donde los datos han sido reemplazados por NaNs. Se usa en grupos de datos donde los ensayos no tienen una longitud fija y tienden a ser largos. |

### MotorTask: TFLA
| Número de columna | Descripción | Notas |
| :--- | :--- | :--- |
| 1 | Número de Bloque dentro de la Ejecución (Run) | |
| 2 | Código de Estímulo del Bloque | 1 - Mano Izquierda, 2 - Pie Izquierdo, 4 - Mano Derecha, 5 - Pie Derecho, 6 - Fijación. |
| 3 | Índice del Ensayo en el Bloque | |
| 4 | Muestra de Inicio del Ensayo (Onset Sample) | |
| 5 | Código de Estímulo del Bloque anterior | |
| 7 | has trial NANs (valores No Numéricos) | Esta bandera se utiliza para indicar si hay segmentos de datos en el ensayo donde los datos han sido reemplazados por NaNs. Se usa en grupos de datos donde los ensayos no tienen una longitud fija y tienden a ser largos. |