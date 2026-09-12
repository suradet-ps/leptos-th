# การจัดการสถานะส่วนกลาง

จนถึงตอนนี้ เราได้ทำงานกับสถานะโลคอลในคอมโพเนนต์เท่านั้น และเราได้เห็นวิธีประสานสถานะระหว่างคอมโพเนนต์แม่กับลูกแล้ว ในบางครั้ง ผู้คนก็มองหาวิธีแก้ปัญหาทั่วไปกว่าสำหรับการจัดการสถานะส่วนกลางที่ใช้ได้ทั่วทั้งแอปพลิเคชัน

โดยทั่วไปแล้ว **คุณไม่จำเป็นต้องอ่านบทนี้** รูปแบบทั่วไปคือการประกอบแอปพลิเคชันของคุณจากคอมโพเนนต์ โดยแต่ละตัวจัดการสถานะโลคอลของตัวเอง ไม่ใช่การเก็บสถานะทั้งหมดไว้ในโครงสร้างส่วนกลาง อย่างไรก็ตาม มีบางกรณี (เช่น การทำธีม การบันทึกการตั้งค่าผู้ใช้ หรือการแชร์ข้อมูลระหว่างคอมโพเนนต์ในส่วนต่างๆ ของ UI) ที่คุณอาจต้องการใช้การจัดการสถานะส่วนกลางรูปแบบใดรูปแบบหนึ่ง

แนวทางที่ดีที่สุดสามประการสำหรับสถานะส่วนกลางคือ

1. ใช้เราเตอร์ขับเคลื่อนสถานะส่วนกลางผ่าน URL
2. ส่งสัญญาณผ่านคอนเท็กซ์
3. สร้างสตรัคต์สถานะส่วนกลางโดยใช้สโตร์

## ทางเลือกที่ 1: URL เป็นสถานะส่วนกลาง

ในหลายแง่ URL จริงๆ แล้วเป็นวิธีที่ดีที่สุดในการเก็บสถานะส่วนกลาง มันเข้าถึงได้จากคอมโพเนนต์ใดก็ได้ ทุกที่ในทรีของคุณ มีเอลิเมนต์ HTML แบบเนทีฟอย่าง `<form>` และ `<a>` ที่มีอยู่เพียงเพื่ออัปเดต URL เท่านั้น และมันคงอยู่ข้ามการรีโหลดหน้าเพจและข้ามอุปกรณ์ คุณสามารถแชร์ URL ให้เพื่อน หรือส่งจากโทรศัพท์ของคุณไปยังแล็ปท็อป และสถานะใดๆ ที่เก็บอยู่ในนั้นจะถูกจำลองขึ้นมาใหม่

ส่วนอีกไม่กี่หัวข้อถัดไปของบทเรียนจะว่าด้วยเราเตอร์ และเราจะลงลึกในหัวข้อเหล่านี้มากกว่านี้

แต่สำหรับตอนนี้ เราจะดูแค่ทางเลือกที่ 2 และ 3

## ทางเลือกที่ 2: การส่งสัญญาณผ่านคอนเท็กซ์

ในหัวข้อว่าด้วย[การสื่อสารระหว่างคอมโพเนนต์แม่กับลูก](view/08_parent_child.md) เราได้เห็นว่าคุณสามารถใช้ `provide_context` เพื่อส่งสัญญาณจากคอมโพเนนต์แม่ไปยังลูก และใช้ `use_context` เพื่ออ่านมันในลูกได้ แต่ `provide_context` ทำงานได้ข้ามระยะทางใดๆ หากคุณต้องการสร้างสัญญาณส่วนกลางที่เก็บสถานะบางอย่าง คุณสามารถ provide มันและเข้าถึงผ่านคอนเท็กซ์ได้ทุกที่ในหมู่ลูกหลานของคอมโพเนนต์ที่คุณ provide มัน

สัญญาณที่ถูก provide ผ่านคอนเท็กซ์จะทำให้เกิดการอัปเดตแบบรีแอกทีฟเฉพาะจุดที่มันถูกอ่านเท่านั้น ไม่ใช่ในคอมโพเนนต์ใดๆ ที่อยู่ระหว่างกลาง ดังนั้นมันจึงคงพลังของการอัปเดตแบบรีแอกทีฟละเอียดไว้ได้ แม้จะอยู่ไกลก็ตาม

เราเริ่มต้นด้วยการสร้างสัญญาณที่รากของแอป และ provide มันให้กับ
children และลูกหลานทั้งหมดโดยใช้ `provide_context`

```rust
#[component]
fn App() -> impl IntoView {
    // here we create a signal in the root that can be consumed
    // anywhere in the app.
    let (count, set_count) = signal(0);
    // we'll pass the setter to specific components,
    // but provide the count itself to the whole app via context
    provide_context(count);

    view! {
        // SetterButton is allowed to modify the count
        <SetterButton set_count/>
        // These consumers can only read from it
        // But we could give them write access by passing `set_count` if we wanted
        <FancyMath/>
        <ListItems/>
    }
}
```

`<SetterButton/>` เป็นตัวนับชนิดที่เราเขียนมาหลายครั้งแล้วตอนนี้

`<FancyMath/>` และ `<ListItems/>` ต่างใช้สัญญาณที่เรา provide ผ่าน
`use_context` และทำอะไรบางอย่างกับมัน

```rust
/// A component that does some "fancy" math with the global count
#[component]
fn FancyMath() -> impl IntoView {
    // here we consume the global count signal with `use_context`
    let count = use_context::<ReadSignal<u32>>()
        // we know we just provided this in the parent component
        .expect("there to be a `count` signal provided");
    let is_even = move || count.get() & 1 == 0;

    view! {
        <div class="consumer blue">
            "The number "
            <strong>{count}</strong>
            {move || if is_even() {
                " is"
            } else {
                " is not"
            }}
            " even."
        </div>
    }
}
```

## ทางเลือกที่ 3: สร้างสโตร์สถานะส่วนกลาง

> เนื้อหาบางส่วนนี้ซ้ำกับหัวข้อว่าด้วยการวนซ้ำข้อมูลที่ซับซ้อนด้วยสโตร์[ที่นี่](view/04b_iteration.md#ทางเลือกที-4-สโตร) ทั้งสองส่วนเป็นเนื้อหาระดับกลาง/ไม่บังคับ ผมจึงคิดว่าการซ้ำกันบ้างคงไม่เป็นไร

สโตร์เป็นพริมิทีฟรีแอกทีฟตัวใหม่ ที่มีให้ใช้ใน Leptos 0.7 ผ่านครีต `reactive_stores` ที่มาคู่กัน (ตอนนี้ครีตนี้ถูกปล่อยแยกออกมา เพื่อให้เราพัฒนาต่อได้โดยไม่ต้องเปลี่ยนเวอร์ชันของเฟรมเวิร์กทั้งหมด)

สโตร์ให้คุณห่อสตรัคต์ทั้งตัว และอ่าน/อัปเดตฟิลด์แต่ละฟิลด์แบบรีแอกทีฟ โดยไม่ติดตามการเปลี่ยนแปลงของฟิลด์อื่น

วิธีใช้คือเพิ่ม `#[derive(Store)]` ให้กับสตรัคต์ (คุณสามารถ `use reactive_stores::Store;` เพื่อนำเข้ามาโครได้) สิ่งนี้จะสร้างแทรตส่วนขยายที่มีเก็ตเตอร์สำหรับแต่ละฟิลด์ของสตรัคต์ เมื่อสตรัคต์ถูกห่อด้วย `Store<_>`

```rust
#[derive(Clone, Debug, Default, Store)]
struct GlobalState {
    count: i32,
    name: String,
}
```

สิ่งนี้สร้างแทรตชื่อ `GlobalStateStoreFields` ซึ่งเพิ่มเมธอด `count` และ `name` ให้กับ `Store<GlobalState>` แต่ละเมธอดคืนค่า*ฟิลด์*ของสโตร์แบบรีแอกทีฟ

```rust
#[component]
fn App() -> impl IntoView {
    provide_context(Store::new(GlobalState::default()));

    // etc.
}

/// A component that updates the count in the global state.
#[component]
fn GlobalStateCounter() -> impl IntoView {
    let state = expect_context::<Store<GlobalState>>();

    // this gives us reactive access to the `count` field only
    let count = state.count();

    view! {
        <div class="consumer blue">
            <button
                on:click=move |_| {
                    *count.write() += 1;
                }
            >
                "Increment Global Count"
            </button>
            <br/>
            <span>"Count is: " {move || count.get()}</span>
        </div>
    }
}
```

การคลิกปุ่มนี้จะอัปเดตเฉพาะ `state.count` เท่านั้น หากเราอ่านจาก `state.name` ที่อื่น
การคลิกปุ่มจะไม่แจ้งเตือนมัน สิ่งนี้ช่วยให้คุณผสานประโยชน์ของโฟลว์ข้อมูลจากบนลงล่าง
เข้ากับการอัปเดตแบบรีแอกทีฟละเอียด

ลองดู[ตัวอย่าง `stores`](https://github.com/leptos-rs/leptos/blob/main/examples/stores/src/lib.rs) ในรีโปสำหรับตัวอย่างที่ครอบคลุมมากกว่านี้
