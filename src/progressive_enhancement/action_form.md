# `<ActionForm/>`

[`<ActionForm/>`](https://docs.rs/leptos/latest/leptos/form/fn.ActionForm.html) คือคอมโพเนนต์ `<Form/>` แบบพิเศษที่รับแอ็กชันฝั่งเซิร์ฟเวอร์ (server action) และจะส่งดิสแพตช์การทำงานนั้นโดยอัตโนมัติเมื่อผู้ใช้ทำการส่งฟอร์ม (form submission) สิ่งนี้ช่วยให้คุณสามารถเรียกใช้ฟังก์ชันฝั่งเซิร์ฟเวอร์ได้โดยตรงจากแท็ก `<form>` แม้ว่าเบราว์เซอร์จะไม่มีหรือไม่รองรับ JS/WASM เลยก็ตาม

ขั้นตอนการใช้งานนั้นเรียบง่ายมาก:

1. นิยามฟังก์ชันฝั่งเซิร์ฟเวอร์โดยใช้ [มาโคร `#[server]`](https://docs.rs/leptos/latest/leptos/attr.server.html) (ดูรายละเอียดใน [ฟังก์ชันฝั่งเซิร์ฟเวอร์](../server/25_server_functions.md))
2. สร้างแอ็กชันขึ้นมาโดยใช้ [`ServerAction::new()`](https://docs.rs/leptos/latest/leptos/server/struct.ServerAction.html) พร้อมทั้งระบุชนิดข้อมูลของฟังก์ชันฝั่งเซิร์ฟเวอร์ที่คุณได้นิยามไว้
3. สร้าง `<ActionForm/>` โดยส่งแอ็กชันฝั่งเซิร์ฟเวอร์เข้าไปทางพร็อพ `action`
4. ส่งผ่านอาร์กิวเมนต์แบบระบุชื่อของฟังก์ชันฝั่งเซิร์ฟเวอร์ ในรูปแบบของฟิลด์อินพุตในฟอร์มที่มีชื่อ (attribute `name`) ตรงกัน

> **หมายเหตุ:** `<ActionForm/>` รองรับเฉพาะการส่งข้อมูลแบบ `POST` ที่เข้ารหัสในรูปแบบ URL-encoded ซึ่งเป็นค่าเริ่มต้นของฟังก์ชันฝั่งเซิร์ฟเวอร์ เพื่อรับประกันการลดทอนประสิทธิภาพอย่างสง่างาม (graceful degradation) และรักษาพฤติกรรมที่ถูกต้องตามมาตรฐานของฟอร์ม HTML

```rust
#[server]
pub async fn add_todo(title: String) -> Result<(), ServerFnError> {
    todo!()
}

#[component]
fn AddTodo() -> impl IntoView {
    let add_todo = ServerAction::<AddTodo>::new();
    // holds the latest *returned* value from the server
    let value = add_todo.value();
    // check if the server has returned an error
    let has_error = move || value.with(|val| matches!(val, Some(Err(_))));

    view! {
        <ActionForm action=add_todo>
            <label>
                "Add a Todo"
                // `title` matches the `title` argument to `add_todo`
                <input type="text" name="title"/>
            </label>
            <input type="submit" value="Add"/>
        </ActionForm>
    }
}
```

การใช้งานนั้นสะดวกและตรงไปตรงมามาก: เมื่อมี JS/WASM ฟอร์มของคุณจะถูกส่งข้อมูลโดยไม่มีการรีโหลดหน้าเว็บใหม่ โดยจะเก็บข้อมูลการส่งครั้งล่าสุดไว้ในสัญญาณ `.input()` ของแอ็กชัน และเก็บสถานะว่ากำลังประมวลผลอยู่หรือไม่ไว้ในสัญญาณ `.pending()` เป็นต้น (หากต้องการทบทวนเพิ่มเติม สามารถดูเอกสารของ [`Action`](https://docs.rs/leptos/latest/leptos/reactive/actions/struct.Action.html)) ในทางกลับกัน หากไม่มี JS/WASM ฟอร์มของคุณจะถูกส่งข้อมูลพร้อมกับการรีโหลดหน้าเว็บตามแบบฉบับเว็บดั้งเดิม และหากคุณมีการเรียกใช้ฟังก์ชัน `redirect` (จาก `leptos_axum` หรือ `leptos_actix`) ระบบจะทำการเปลี่ยนเส้นทางไปยังหน้าที่ถูกต้องให้ หรือโดยค่าเริ่มต้นก็จะรีเฟรชกลับมาที่หน้าเดิมที่คุณกำลังเปิดอยู่ พลังของ HTML, HTTP และการเรนเดอร์แบบไอโซมอร์ฟิกทำให้ `<ActionForm/>` ของคุณสามารถทำงานได้จริงในทุกสถานการณ์ แม้จะปราศจาก JS/WASM โดยสิ้นเชิง

## การตรวจสอบความถูกต้องฝั่งไคลเอนต์

เนื่องจาก `<ActionForm/>` แท้จริงแล้วก็คือแท็ก `<form>` ธรรมดา มันจึงปล่อยเหตุการณ์ (event) `submit` ออกมาตามปกติ คุณจึงสามารถเลือกใช้ทั้งการตรวจสอบความถูกต้องของ HTML ในตัว หรือเขียนลอจิกการตรวจสอบความถูกต้องบนฝั่งไคลเอนต์ของคุณเองผ่านตัวจัดการเหตุการณ์ `on:submit:capture` ได้ โดยเพียงเรียก `ev.prevent_default()` หากต้องการยกเลิกการส่งฟอร์ม

แทรต [`FromFormData`](https://docs.rs/leptos/latest/leptos/form/trait.FromFormData.html) มีประโยชน์อย่างมากในจุดนี้ สำหรับใช้แปลงข้อมูลจากฟอร์มที่ส่งเข้ามา ให้กลายเป็นชนิดข้อมูลโครงสร้างของฟังก์ชันฝั่งเซิร์ฟเวอร์ของคุณโดยอัตโนมัติ

```rust
let on_submit = move |ev| {
	let data = AddTodo::from_event(&ev);
	// silly example of validation: if the todo is "nope!", nope it
	if data.is_err() || data.unwrap().title == "nope!" {
		// ev.prevent_default() will prevent form submission
		ev.prevent_default();
	}
}

// ... add the `submit` handler to an `ActionForm`

<ActionForm on:submit:capture=on_submit /* ... */>
```

```admonish note
โปรดสังเกตว่าเราเลือกใช้ `on:submit:capture` แทนที่จะเป็น `on:submit` แบบปกติ ทั้งนี้เพื่อผูกตัวรับฟังเหตุการณ์ให้อยู่ในช่วง capture phase ของเบราว์เซอร์ แทนที่จะเป็นช่วง bubbling phase ซึ่งหมายความว่าตัวจัดการเหตุการณ์ของคุณจะทำงานก่อนตัวจัดการ `submit` ในตัวของ `ActionForm` เสมอ สามารถศึกษาข้อมูลเพิ่มเติมได้จาก [issue นี้](https://github.com/leptos-rs/leptos/issues/3872)
```

## อินพุตที่ซับซ้อน

ในกรณีที่อาร์กิวเมนต์ของฟังก์ชันฝั่งเซิร์ฟเวอร์เป็นโครงสร้างสตรักต์ที่มีฟิลด์ซ้อนกันภายในหลายชั้น (nested serializable fields) คุณควรใช้รูปแบบการระบุชื่อดัชนี (indexing notation) ตามมาตรฐานของ `serde_qs`:

```rust
#[derive(serde::Serialize, serde::Deserialize, Debug, Clone)]
struct Settings {
    display_name: String,
}

#[derive(serde::Serialize, serde::Deserialize, Debug, Clone)]
struct HeftyData {
    first_name: String,
    last_name: String,
    settings: Settings,
}

#[component]
fn ComplexInput() -> impl IntoView {
    let submit = ServerAction::<VeryImportantFn>::new();

    view! {
      <ActionForm action=submit>
        <input type="text" name="hefty_arg[first_name]" value="leptos"/>
        <input
          type="text"
          name="hefty_arg[last_name]"
          value="closures-everywhere"
        />
        <input
          type="text"
          name="hefty_arg[settings][display_name]"
          value="my alias"
        />
        <input type="submit"/>
      </ActionForm>
    }
}

#[server]
async fn very_important_fn(hefty_arg: HeftyData) -> Result<(), ServerFnError> {
    assert_eq!(hefty_arg.first_name.as_str(), "leptos");
    assert_eq!(hefty_arg.last_name.as_str(), "closures-everywhere");
    aseert_eq!(hefty_arg.settings.display_name.as_str(), "my alias");
    Ok(())
}
```
