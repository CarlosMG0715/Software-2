const FAQ = [
  ["¿Mi reseña es anónima?", "Tu identidad no se muestra públicamente ni al docente. La aplicación usa un seudónimo criptográfico para asociar la reseña con tu cuenta; no es anonimato absoluto: quien tenga acceso a la base de datos y al secreto del servidor podría correlacionarlos."],
  ["¿Cuántas reseñas puedo escribir por docente?", "Una por docente, materia y periodo. Puedes editarla o eliminarla cuando quieras."],
  ["¿Qué pasa si reportan una reseña?", "El reporte entra en la cola de moderación. Un moderador revisa el caso y decide si aprueba, rechaza o elimina la reseña; los reportes por sí solos no la ocultan."],
  ["¿Cuándo se publica una reseña?", "Las reseñas nuevas y las que se editan quedan pendientes hasta que un moderador las apruebe."],
  ["¿Cómo se califica?", "Claridad, exigencia y puntualidad de 1 a 5; la escala se explica en cada criterio del formulario."],
  ["¿Qué datos personales se tratan?", "Tu correo institucional, bajo la Ley 1581 de 2012, solo para autenticarte."],
];

export default function Ayuda() {
  return (
    <>
      <h1>Ayuda y preguntas frecuentes</h1>
      {FAQ.map(([q, a]) => (
        <details key={q} className="tarjeta"><summary>{q}</summary><p>{a}</p></details>
      ))}
    </>
  );
}
